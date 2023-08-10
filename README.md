# spotify-data-pipeline

Certainly! Below is an example GitHub README for your recently played songs data retrieval and storage script. Feel free to customize it further to match your project's details and requirements.

---

# Recently Played Songs Data Retrieval and Storage

This repository contains a Python script that interacts with the Spotify API to retrieve recently played songs and stores them in a SQLite database. The script is organized as a Prefect flow, ensuring a well-structured and efficient data processing workflow.

## Features

- Fetches recently played songs data from the Spotify API.
- Uses SQLAlchemy to store the data in a SQLite database.
- Utilizes Prefect to manage data flow and tasks execution.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a valid Spotify developer account.
- You have obtained your Spotify Client ID and Client Secret.
- You have generated a Spotify Refresh Token for authentication.
- Python 3.x is installed on your system.
- You have set up a virtual environment (recommended).

## Setup and Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/recently-played-songs.git
   cd recently-played-songs
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file in the project directory and adding the following:

   ```ini
   SPOTIFY_CLIENT_ID=your-client-id
   SPOTIFY_CLIENT_SECRET=your-client-secret
   SPOTIFY_REFRESH_TOKEN=your-refresh-token
   ```

4. Run the Prefect flow to retrieve and store recently played songs:

   ```bash
   python your_script_name.py
   ```

## Workflow Explanation

1. **Refresh Access Token:** Retrieves a new access token using the provided Spotify Client ID, Client Secret, and Refresh Token.

2. **Get Latest Played At:** Queries the SQLite database to get the latest played_at timestamp, which is used as the starting point for data retrieval.

3. **Retrieve Songs Data:** Makes a request to the Spotify API to fetch recently played songs data, using the access token obtained in the first step.

4. **Transform and Insert Songs:** Transforms the fetched data and inserts it into the SQLite database as records in the `recently_played_songs` table.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for any improvements or fixes you'd like to propose.

## License

This project is licensed under the [MIT License](LICENSE).

---

Replace placeholders (`your-username`, `your-client-id`, `your-client-secret`, `your-refresh-token`, `your_script_name.py`, etc.) with actual values and filenames. Additionally, add any additional sections or information that you think are relevant to your project.

Remember to update the `LICENSE` file with the appropriate license text if you choose a different license for your project.

Feel free to enhance and customize this README according to your project's needs and style!
