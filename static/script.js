document.addEventListener('DOMContentLoaded', () => {
    const buzzButton = document.getElementById('buzzButton');
    const teamInput = document.getElementById('teamName');
    const result = document.getElementById('result');
    const resetButton = document.getElementById('resetButton');
    const statusSpan = document.getElementById('status');
    const firstTeamSpan = document.getElementById('firstTeam');

    // Handle Buzzer Press
    if (buzzButton) {
        buzzButton.addEventListener('click', async () => {
            const teamName = teamInput.value.trim();
            if (!teamName) {
                result.innerText = "Please enter a team name!";
                return;
            }

            const response = await fetch('/buzz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ team_name: teamName })
            });

            const data = await response.json();
            result.innerText = data.status === 'Success' ? 
                `You buzzed first: ${data.first_team}` : 
                "Buzzer is inactive or already pressed!";
        });
    }

    // Handle Admin Reset
    if (resetButton) {
        resetButton.addEventListener('click', async () => {
            const response = await fetch('/reset', { method: 'POST' });
            const data = await response.json();
            alert(data.status);
            updateStatus();
        });
    }

    // Periodically Check Buzzer Status
    async function updateStatus() {
        const response = await fetch('/status');
        const data = await response.json();

        if (statusSpan) statusSpan.innerText = data.buzzer_active ? 'Active' : 'Inactive';
        if (firstTeamSpan) firstTeamSpan.innerText = data.first_team || 'None';
    }

    // Update status every second for admin panel
    if (resetButton) {
        setInterval(updateStatus, 1000);
    }
});
