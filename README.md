# holdmybeer.fun / SOON 🍺

![project](/src/frontend/assets/preview.png)

A simple, fun, and easy-to-use web application for sharing temporary links and images.

## Features
- **Temporary Links**: Share links that expire after a certain period of time.
- **Image Upload**: Upload and share images with a simple drag-and-drop interface.
- **User-Friendly Interface**: A clean and intuitive design for easy navigation.
- **One-Use Links**: Create links that can only be used once.
- **No Registration Required**: Share links and images without the need for an account.
- **Fast and Secure**: Built with FastAPI for speed and security.

## Tech Stack
- **Backend**: Python, FastAPI, PostgreSQL, Redis, Docker and more
- **Frontend**: Idk, but it's a mess
- **Deployment**: Docker, Nginx

## How to Run

<details>
<summary>Manual Run (poetry)</summary>

1. Clone the repository. 

2. Install the dependencies `poetry install`

3. Create a `.env` file and add the following variables from `.env.example` file

4. Run the migrations `poetry run alembic upgrade head`

5. Run the server

</details>

<details>
<summary>Docker Run</summary>

1. Clone the repository.

2. Create a `.env` file and add the following variables from `.env.example` file

3. Run the docker compose `docker-compose up --build -d`

</details>