from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "buzzer_secret_key_change_this_in_production"  # Required for session management

# Global variables to manage buzzer state
buzzer_active = False
timer_active = False
remaining_time = 0
buzzed_teams = []
team_names = {}  # Dictionary to store team ID to name mappings

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
        team_id = request.form.get('team_id')
        team_name = request.form.get('team_name')
        
        if team_id and team_name:
            team_names[team_id] = team_name
            session['team_id'] = team_id  # Store team ID in session
            return redirect(url_for('team_page'))
    
    return render_template('team_selection.html', default_teams=default_teams)

@app.route('/team', methods=['GET'])
def team_page():
    team_id = session.get('team_id')
    
    if not team_id:
        return redirect(url_for('team_selection'))
    
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
    return jsonify({"status": "Success", "message": "Buzzer reset successfully"})

@app.route('/toggle-buzzer', methods=['POST'])
def toggle_buzzer():
    global buzzer_active
    buzzer_active = not buzzer_active
    return jsonify({"status": "Success", "buzzer_active": buzzer_active})

@app.route('/set-timer', methods=['POST'])
def set_timer():
    global timer_active, remaining_time, buzzer_active
    
    seconds = request.json.get('seconds', 0)
    remaining_time = int(seconds)
    timer_active = True
    buzzer_active = True
    
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
    
    team_name = team_names.get(team_id, "Unknown Team")
    
    if not buzzer_active:
        return jsonify({"status": "Error", "message": "Buzzer not active"}), 400
    
    if team_name in buzzed_teams:
        return jsonify({"status": "Error", "message": "Your team already buzzed in"}), 400
    
    buzzed_teams.append(team_name)
    position = len(buzzed_teams)
    
    return jsonify({
        "status": "Success", 
        "message": f"Buzzed in at position {position}",
        "position": position
    })

@app.route('/update-team-name', methods=['POST'])
def update_team_name():
    team_id = request.json.get('team_id')
    new_name = request.json.get('new_name')
    
    if not team_id or not new_name:
        return jsonify({"status": "Error", "message": "Team ID and new name required"}), 400
    
    team_names[team_id] = new_name
    return jsonify({"status": "Success", "message": "Team name updated successfully"})

if __name__ == '__main__':
    app.run(debug=True)