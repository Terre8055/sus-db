#!/bin/bash

# Display ASCII art
cat << "EOF"
WELCOME TO SUS DB
    _   _____________ _______  ____  ____  __   ______
   / | / / ____/ ___// ____/ |/_/ / / / / /  / ____/
  /  |/ / __/  \__ \/ /    >  <  / / / / /  / /     
 / /|  / /___ ___/ / /____/ / / /_/ /_/ /  / /___   
/_/ |_/_____//____/\____/_/ /_/\____/_/   \____/   

Author: Michael Appiah Dankwah
GitHub: @Terre8055

EOF

# Display large ASCII art
cat << "EOF"
 __   __   __   ______   ______   ______   ______   ______      ______   ______      ______   __  __   ______   _____    ______  
/\ \ / /  /\ \ /\  ___\ /\  ___\ /\  ___\ /\  __ \ /\  ___\    /\__  _\ /\  __ \    /\  ___\ /\ \/\ \ /\  ___\ /\  __-. /\  == \ 
\ \ \'/   \ \ \\ \  __\ \ \ \____\ \ \____\ \ \/\ \\ \___  \   \/_/\ \/ \ \ \/\ \   \ \___  \\ \ \_\ \\ \___  \\ \ \/\ \\ \  __< 
 \ \__|    \ \_\\ \_____\\ \_____\\ \_____\\ \_____\\/\_____\     \ \_\  \ \_____\   \/\_____\\ \_____\\/\_____\\ \____- \ \_\ \_\
  \/_/      \/_/ \/_____/ \/_____/ \/_____/ \/_____/ \/_____/      \/_/   \/_____/    \/_____/ \/_____/ \/_____/ \/____/  \/_/ /_/
EOF

# Start the Flask server
echo "Starting SusDB server..."
python3 src/susdb_server.py &

# Wait for the server to start
sleep 2

# Display server information
cat << EOF

SusDB server is now running on http://localhost:8000

Available endpoints:
  POST /store    - Store a user string
  POST /verify   - Verify user credentials
  POST /view     - View user database
  POST /retrieve - Retrieve user data
  POST /close    - Close user account

Use the SusDB CLI or send HTTP requests to interact with the database.
Type 'python /app/src/susdb_cli.py --help' for CLI usage information.
EOF

# Keep the container running
tail -f /dev/null
