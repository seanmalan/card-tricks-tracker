# Prestige — Card Magic Tracker

A personal app for tracking your card magic practice. Log sessions, track moves and tricks, monitor progress, and see what needs brushing up — all from any device on your home network.

---

## What You Need Before Starting

You need two free programs installed on your computer:

- **Git** — downloads the app files from the internet
- **Docker Desktop** — runs the app (no other software needed)

Follow the steps below for your operating system.

---

## Windows Setup

### Step 1 — Install Git

1. Open your web browser and go to: **https://git-scm.com/download/win**
2. The download should start automatically. If not, click the link for **64-bit Git for Windows Setup**
3. Open the downloaded file and run the installer
4. Keep clicking **Next** on every screen — the default options are all fine
5. Click **Finish** when done

To check it worked:
- Press the **Windows key**, type `cmd`, press Enter to open Command Prompt
- Type `git --version` and press Enter
- You should see something like `git version 2.44.0` — that means it's working

---

### Step 2 — Install Docker Desktop

1. Go to: **https://www.docker.com/products/docker-desktop**
2. Click **Download for Windows**
3. Open the downloaded file and run the installer
4. Keep the default options and click **OK / Next** throughout
5. When it finishes it will ask you to **restart your computer** — do that
6. After restarting, Docker Desktop will open automatically
7. You may be asked to accept the terms — click **Accept**
8. Wait until you see the Docker whale icon in the taskbar (bottom right of your screen) — when it stops animating it means Docker is ready

> **Note:** During install, Docker may ask about **WSL 2**. If a window pops up asking you to install it, click the link it provides and follow the steps — then restart again and reopen Docker Desktop.

To check it worked:
- Open Command Prompt (Windows key → type `cmd` → Enter)
- Type `docker --version` and press Enter
- You should see something like `Docker version 26.0.0`

---

### Step 3 — Download and Run the App

1. Open **Command Prompt** (Windows key → type `cmd` → Enter)
2. Type the following commands one at a time, pressing Enter after each:

```
git clone https://github.com/seanmalan/card-tricks-tracker.git
```

```
cd card-tricks-tracker
```

```
docker compose up -d
```

3. The first time you run this it will download everything needed — this may take a few minutes depending on your internet. You will see a lot of text scrolling — that is normal.
4. When it finishes and you get your prompt back, the app is running.

---

### Step 4 — Open the App

1. Open any web browser (Chrome, Edge, Safari, Firefox)
2. In the address bar at the top, type:

```
http://localhost:5757
```

3. Press Enter — the app will open

**Bookmark this address** so you can get back to it easily.

---

## Mac Setup

### Step 1 — Install Git

1. Open **Terminal** — press **Command + Space**, type `Terminal`, press Enter
2. Type the following and press Enter:

```
xcode-select --install
```

3. A popup window will appear — click **Install**
4. Wait for it to finish (a few minutes)
5. To check it worked, type `git --version` — you should see a version number

---

### Step 2 — Install Docker Desktop

1. Go to: **https://www.docker.com/products/docker-desktop**
2. Click **Download for Mac**
3. Choose the right version for your Mac:
   - If your Mac is from **2020 or newer**, choose **Apple Silicon**
   - If your Mac is older, choose **Intel**
   - Not sure? Click the Apple menu (top left) → **About This Mac** — if it says "Apple M1/M2/M3/M4" choose Apple Silicon, otherwise choose Intel
4. Open the downloaded `.dmg` file
5. Drag the Docker icon into your **Applications** folder
6. Open Docker from Applications
7. It will ask for your **Mac password** to finish installing — enter it
8. Wait until the Docker whale icon appears in the menu bar (top right of screen) and says **Docker Desktop is running**

To check it worked:
- Open Terminal and type `docker --version`
- You should see something like `Docker version 26.0.0`

---

### Step 3 — Download and Run the App

1. Open **Terminal** (Command + Space → type Terminal → Enter)
2. Type the following commands one at a time, pressing Enter after each:

```
git clone https://github.com/seanmalan/card-tricks-tracker.git
```

```
cd card-tricks-tracker
```

```
docker compose up -d
```

3. The first time this runs it will download everything — this takes a few minutes. Lots of text will scroll past — that is normal.
4. When it finishes and you see your prompt again, the app is running.

---

### Step 4 — Open the App

1. Open any web browser (Safari, Chrome, Firefox)
2. In the address bar, type:

```
http://localhost:5757
```

3. Press Enter — the app will open

**Bookmark this address** so you can get back to it easily.

---

## Updating the App

When a new version is available, run the included update script — it pulls the latest code and rebuilds the Docker image in one step.

**Mac:**
1. Open Terminal, go to your `card-tricks-tracker` folder
2. Run:
   ```
   ./update.sh
   ```

**Windows:**
1. Open the `card-tricks-tracker` folder in File Explorer
2. Double-click `update.bat`

> **Important:** Plain `docker compose up -d` does NOT rebuild the image — it reuses whatever was built last time. The update script runs `docker compose up -d --build` for you.

Your data (the `data/tricks.db` file) is left alone — updates never touch it.

---

## Starting the App After a Restart

If you restart your computer, Docker Desktop needs to be running for the app to work. It should start automatically, but if the app isn't loading:

1. Open **Docker Desktop** from your Applications (Mac) or Start Menu (Windows)
2. Wait for it to say **Docker Desktop is running**
3. Go back to your browser and try `http://localhost:5757` again

If it still doesn't load, open Terminal / Command Prompt and run:

```
cd card-tricks-tracker
docker compose up -d
```

---

## Using the App

### Dashboard
The home screen shows an overview of your practice:
- **Total sessions, hours, moves and tricks** tracked
- **Practice frequency chart** — a bar for each of the last 30 days
- **Needs Brushing Up** — tricks you haven't practiced recently
- **Tricks in Progress** and **Moves Needing Work**

### Sessions
Log a practice session with:
- Date and duration (or use the built-in timer)
- What you focused on
- Which moves you worked on
- Notes and a quality rating

Click any session to view the full details or delete it.

### Moves & Sleights
Track individual techniques — Double Lifts, passes, controls, shuffles and so on. Set a skill level (Beginner → Performance Ready) and confidence rating, and add notes and your reference source.

### Tricks & Routines
Track complete tricks and routines. Each trick has:
- A status (Learning / Drilling / Performance Ready / Retired)
- A tutorial link you can click to go straight to the video or resource
- Moves used, source/creator, and performance notes
- A **✓ Practiced Today** button — click this after working on the trick to keep your practice dates up to date

### Practice Timer
A stopwatch you can run during a session. When you stop it, you can log it directly as a practice session.

### Settings
Set how many days before a trick shows up in the **Needs Brushing Up** section on the dashboard. Default is 14 days.

---

## Accessing from Your Phone or Other Devices

If you want to use the app from your phone or another laptop on the same home Wi-Fi:

1. Find the IP address of the computer running the app:
   - **Windows:** Open Command Prompt and type `ipconfig` — look for **IPv4 Address** under your Wi-Fi adapter, something like `192.168.1.30`
   - **Mac:** System Settings → Wi-Fi → click your network → look for **IP Address**
2. On your phone or other device, open a browser and go to:

```
http://192.168.1.XX:5757
```

(Replace `192.168.1.XX` with the actual IP address from step 1)

---

## Troubleshooting

**The app won't open / page not found**
- Make sure Docker Desktop is running (whale icon in taskbar/menu bar)
- Open Terminal / Command Prompt, go to the `card-tricks-tracker` folder and run `docker compose up -d`

**I closed the Terminal — is the app still running?**
- Yes. Once started with `docker compose up -d` it runs in the background. You don't need to keep Terminal open.

**How do I stop the app?**
- Open Terminal / Command Prompt, go to the `card-tricks-tracker` folder and run `docker compose down`

**My data — will it be lost if I update the app?**
- No. All your data is stored in a file called `tricks.db` inside the `data` folder in your `card-tricks-tracker` folder. It is never touched when you update or restart the app.
