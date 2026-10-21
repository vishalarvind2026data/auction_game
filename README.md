# Real-Time English Auction (`live_auction`)

An oTree app implementing a 60-second real-time English auction with a built-in trading floor chat and budget constraints.

## Auction Parameters

| Parameter | Value | Where |
|---|---|---|
| Group size | 3 or 4 players | `C.PLAYERS_PER_GROUP` (default 4) |
| Starting bid | 10 € | `C.STARTING_BID` |
| Player budget | 80 € | `C.BUDGET` |
| Item value | 100 € | `C.ITEM_VALUE` |
| Duration | 60 s | `timeout_seconds = 60` on the `Decision` page |

## Environment Setup

Use a Miniconda/conda environment with Python 3.11:

```bash
conda create -n otree_env python=3.11 -y
conda activate otree_env
pip install -U otree
otree --version
```

## How to Run

### 1. Local Testing (Single Machine)

Activate the conda environment, navigate to the project directory, and start the development server:

```bash
# Activate conda environment (otree_env or otreeenv)
conda activate otree_env

# Navigate to project directory
cd "/Users/arvind_govindaraj/Downloads/live auction/otree_live_auction"

# Start local server
otree devserver
```

Open `http://localhost:8000` in your browser and click on **Real-Time English Auction** in the demo list.

### 2. Multi-Device / LAN Testing (Wi-Fi, Tablets, Other Laptops)

To let other devices on the same Wi-Fi/local network access the auction:

1. **Find your local IP address:**
   - **macOS (Terminal / Bash):**
     ```bash
     ipconfig getifaddr en0
     ```
     *(Alternative: `ifconfig | grep "inet "`)*
   - **Windows (Command Prompt):**
     ```cmd
     ipconfig
     ```

2. **Run devserver bound to your network:**
   ```bash
   # Listen on all network interfaces:
   otree devserver 0.0.0.0:8000

   # Or bind directly to your local IP (e.g. 10.50.3.17):
   otree devserver <your_ip_address>:8000
   ```

3. **Access from other devices:**
   Open `http://<your_ip_address>:8000` (e.g. `http://10.50.3.17:8000`) in the web browser on any connected phone, tablet, or laptop.

## Server Rules, Payoffs, and Chat

The auction logic is handled by `live_method` on the server: a bid is accepted only if `bid > group.highest_bid` and `bid <= C.BUDGET`. Valid bids immediately update the group's highest bid and leader and are broadcast to all group members using `{0: ...}`. Invalid bids return a private error message `{player.id_in_group: {"error": "Invalid bid"}}` solely to the sender. When the 60-second countdown timer expires, `before_next_page` calculates the payoffs: the winning bidder receives `C.BUDGET - group.highest_bid + C.ITEM_VALUE` (i.e. keeps remaining budget plus the 100 € item value), while all other players retain their full `C.BUDGET` (80 €). If nobody bids, all players receive their 80 € budget. The interface features a real-time trading floor chat powered by oTree's `{{ chat }}` tag scoped to the group.

## Multi-Window Testing Guide

1. Navigate to `http://localhost:8000` and launch the **Real-Time English Auction** demo.
2. Open the 4 participant links in separate browser windows (or private/incognito windows) to simulate distinct players.
3. Advance through the Instructions page to the start wait page until all 4 players synchronize.
4. Execute test cases:
   - **Test 1**: Player 1 submits a bid of 20 €. All windows immediately update to show 20 € and "Player 1" as leader ("Player 1 (you)" in Player 1's window).
   - **Test 2**: Player 2 submits 20 € (equal bid). Player 2 sees a private "Invalid bid" error; others see no error.
   - **Test 3**: Player 2 submits 81 € (exceeds budget). Player 2 sees "Invalid bid"; highest bid remains unchanged.
   - **Test 4**: Player 2 submits 35 €. All windows update to show 35 € and Player 2 as the new leader.
   - **Test 5**: Pressing Enter in the bid input sends the bid and does not submit the form.
   - **Test 6**: Refreshing/reloading a window mid-auction recovers the current bid and leader via the `sync` message.
   - **Test 7**: Send chat messages across windows and verify they appear instantly for all group members.
   - **Test 8**: Allow the 60-second timer to expire; all players advance to the Results page.
   - **Test 9**: Verify payoffs: with winning bid 35 €, winner payoff = 80 - 35 + 100 = 145 €, non-winners = 80 €.
   - **Test 10**: Run an auction where no player places a bid; verify the "Nobody placed a valid bid" notice appears and all payoffs are 80 €.
