from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import logging
from datetime import datetime

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "buzzer_secret_key_change_this_in_production")

# Global variables to manage buzzer state
buzzer_active = False
timer_active = False
remaining_time = 0
buzzed_teams = []  # List of dictionaries with team info and timestamp
team_names = {}  # Dictionary to store team ID to name mappings
removed_teams = set()  # Set to store IDs of teams that have been removed

# Default team names from popular story game characters
default_teams = [
    "Geralt of Rivia", "Arthur Morgan", "Booker DeWitt", "Commander Shepard", "Joel Miller",
    "Kratos", "Nathan Drake", "Solaire of Astora", "Eileen the Crow", "The Tarnished",
    "Dragonborn", "Vault Dweller", "V from Cyberpunk", "Aloy", "Jin Sakai",
    "Sam Porter Bridges", "Ezio Auditore", "Corvo Attano", "Jack of Fable", "Lee Everett",
    "Max Caulfield", "Ethan Mars", "Connor (Detroit: Become Human)", "Henry (Firewatch)", "Alex (Oxenfree)"
]

@app.route('/')
def index():
    return redirect(url_for('team_selection'))

@app.route('/team-selection', methods=['GET', 'POST'])
def team_selection():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        
        if team_name:
            # Auto-generate team ID based on team name and timestamp for uniqueness
            import time
            import re
            timestamp = int(time.time() * 1000)  # milliseconds
            clean_name = re.sub(r'[^a-z0-9_]', '', team_name.lower().replace(' ', '_'))[:10]
            team_id = f"{clean_name}_{timestamp}"
            
            # Check if team was previously removed
            if team_id in removed_teams:
                removed_teams.remove(team_id)  # Allow them to rejoin
            
            team_names[team_id] = team_name
            session['team_id'] = team_id  # Store team ID in session
            logging.info(f"Team '{team_name}' joined with auto-generated ID: {team_id}")
            return redirect(url_for('team_page'))
    
    return render_template('team_selection.html')

@app.route('/team', methods=['GET'])
def team_page():
    team_id = session.get('team_id')
    if not team_id:
        return redirect(url_for('team_selection'))
    
    # Check if team has been removed
    if team_id in removed_teams:
        return render_template('team_removed.html')
    
    team_name = team_names.get(team_id, "Unknown Team")
    return render_template('team.html', team_name=team_name)

@app.route('/admin')
def admin_page():
    return render_template('admin.html',
                         buzzer_active=buzzer_active,
                         buzzed_teams=buzzed_teams,
                         team_names=team_names)

@app.route('/reset', methods=['POST'])
def reset():
    global buzzer_active, buzzed_teams
    buzzer_active = False
    buzzed_teams = []
    logging.info("Buzzer reset - all teams cleared")
    return jsonify({"status": "Success", "message": "Buzzer reset successfully"})

@app.route('/toggle-buzzer', methods=['POST'])
def toggle_buzzer():
    global buzzer_active
    buzzer_active = not buzzer_active
    logging.info(f"Buzzer toggled - now {'active' if buzzer_active else 'inactive'}")
    return jsonify({"status": "Success", "buzzer_active": buzzer_active})

@app.route('/set-timer', methods=['POST'])
def set_timer():
    global timer_active, remaining_time, buzzer_active
    seconds = request.json.get('seconds', 0)
    remaining_time = int(seconds)
    timer_active = True
    buzzer_active = True
    logging.info(f"Timer set to {remaining_time} seconds")
    return jsonify({
        "status": "Success",
        "remaining_time": remaining_time,
        "timer_active": timer_active
    })

@app.route('/update-timer', methods=['POST'])
def update_timer():
    global timer_active, remaining_time, buzzer_active
    action = request.json.get('action')
    
    if action == 'start':
        timer_active = True
    elif action == 'pause':
        timer_active = False
    elif action == 'reset':
        timer_active = False
        remaining_time = 0
        buzzer_active = False
    elif action == 'tick':
        if timer_active and remaining_time > 0:
            remaining_time -= 1
            if remaining_time == 0:
                timer_active = False
                buzzer_active = False
    
    return jsonify({
        "status": "Success",
        "remaining_time": remaining_time,
        "timer_active": timer_active,
        "buzzer_active": buzzer_active
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "buzzer_active": buzzer_active,
        "timer_active": timer_active,
        "remaining_time": remaining_time,
        "buzzed_teams": buzzed_teams,
        "team_names": team_names
    })

@app.route('/team-status', methods=['GET'])
def team_status():
    team_id = session.get('team_id')
    if not team_id:
        return jsonify({"status": "Error", "message": "No team identified"}), 401
    
    return jsonify({
        "removed": team_id in removed_teams
    })

@app.route('/timer-status', methods=['GET'])
def timer_status():
    return jsonify({
        "timer_active": timer_active and buzzer_active,
        "remaining_time": remaining_time
    })

@app.route('/buzz', methods=['POST'])
def buzz():
    team_id = session.get('team_id')
    if not team_id:
        return jsonify({"status": "Error", "message": "No team identified"}), 401
    
    if team_id in removed_teams:
        return jsonify({"status": "Error", "message": "Your team has been removed from the game"}), 403
    
    team_name = team_names.get(team_id, "Unknown Team")
    
    if not buzzer_active:
        return jsonify({"status": "Error", "message": "Buzzer not active"}), 400
    
    # Check if team already buzzed in
    team_already_buzzed = any(team['name'] == team_name for team in buzzed_teams)
    if team_already_buzzed:
        return jsonify({"status": "Error", "message": "Your team already buzzed in"}), 400
    
    # Add team to buzzed list with timestamp - NO LIMIT ON NUMBER OF TEAMS
    buzz_time = datetime.now()
    buzzed_teams.append({
        'name': team_name,
        'team_id': team_id,
        'timestamp': buzz_time,
        'formatted_time': buzz_time.strftime("%H:%M:%S")
    })
    
    position = len(buzzed_teams)
    
    # Get ordinal suffix for position display
    def get_ordinal_suffix(n):
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    position_text = get_ordinal_suffix(position)
    
    logging.info(f"Team {team_name} buzzed in at position {position}")
    
    return jsonify({
        "status": "Success",
        "message": f"Buzzed in at {position_text} position!",
        "position": position,
        "position_text": position_text
    })

@app.route('/update-team-name', methods=['POST'])
def update_team_name():
    team_id = request.json.get('team_id')
    new_name = request.json.get('new_name')
    
    if not team_id or not new_name:
        return jsonify({"status": "Error", "message": "Team ID and new name required"}), 400
    
    old_name = team_names.get(team_id)
    team_names[team_id] = new_name
    
    # Update the name in buzzed_teams list if the team has already buzzed
    for team in buzzed_teams:
        if team['team_id'] == team_id:
            team['name'] = new_name
    
    logging.info(f"Team name updated from {old_name} to {new_name}")
    return jsonify({"status": "Success", "message": "Team name updated successfully"})

@app.route('/remove-team', methods=['POST'])
def remove_team():
    team_id = request.json.get('team_id')
    
    if not team_id:
        return jsonify({"status": "Error", "message": "Team ID required"}), 400
    
    if team_id in team_names:
        team_name = team_names[team_id]
        
        # Remove from buzzed teams if present
        buzzed_teams[:] = [team for team in buzzed_teams if team['team_id'] != team_id]
        
        # Add to removed teams set
        removed_teams.add(team_id)
        
        # Remove from team_names dictionary
        del team_names[team_id]
        
        logging.info(f"Team {team_name} (ID: {team_id}) removed")
        
        return jsonify({
            "status": "Success",
            "message": f"Team {team_name} (ID: {team_id}) has been removed",
            "team_name": team_name
        })
    else:
        return jsonify({"status": "Error", "message": "Team ID not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
