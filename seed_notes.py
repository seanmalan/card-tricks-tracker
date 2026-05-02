"""Starter step-by-step notes for the canonical tricks in the seed library.

These are general descriptions of well-known public methods — enough to give
the dad a structured starting point. He's expected to overwrite them with his
own routines, scripting, and handling. Run via:

    docker compose exec card-tricks python3 seed.py --seed-notes

The seeder ONLY fills in notes that are currently empty, so anything the user
has already written is left alone.

Tricks not listed here are skipped (either too proprietary to summarise or
have many radically different methods).
"""

STARTER_NOTES = {
    "Ambitious Card": """\
EFFECT
A signed card repeatedly rises to the top of the deck, no matter how it's lost.

A WORKING STRUCTURE (Daryl-style, eight phases)
1. Card returned to the middle. Snap, double-lift reveals it on top.
2. Card placed in the middle face-up. Turn the deck over — selection is face-down on top.
3. Tilt phase: card apparently pushed deep into the deck (Marlo's Tilt). Snap, on top.
4. Card cut into the deck. Use a top change in the cut — on top.
5. Spectator pushes the card into the deck themselves. Cut, riffle, on top.
6. Card placed third from the top, pushed flush in the middle. Still third from top.
7. Card stabbed face-up into the middle with another card. Jiggle, turn over the deck — selection.
8. KICKER: card vanishes from the deck, found in pocket / wallet / signed envelope.

CORE MOVES
Double Lift · Tilt (Marlo) · Top Change · Pass · Side Steal · Card to Pocket
Bottom Deal (optional, for a fairer-looking phase)

PERFORMANCE
- Vary the methods — never use the same move two phases in a row.
- Each phase should feel like the climax, then top it.
- The signature on the card is the moment that ties it all together.
- Pace it. Don't rush. Let each rise breathe.
""",

    "Triumph": """\
EFFECT
The deck is genuinely shuffled face-up into face-down. A selected card is found, the deck rights itself, and the selection is the only reversed card in the otherwise face-down pack.

METHOD (Vernon's classic)
1. Ribbon spread. Spectator selects, notes, signs the card.
2. Card returned to deck under cover.
3. Strip out roughly half the deck and flip it face-up.
4. The Triumph Shuffle (Zarrow is the gold standard): apparently mixes face-up
   into face-down, actually preserves the orientation of both halves.
5. Spread or fan: cards still appear mixed.
6. Slip-cut / pass to bring the selection adjacent to the orientation break.
7. Snap the deck flat. Ribbon spread face-up — every card has righted itself
   except the selection, which is reversed in the middle.

CORE MOVES
Zarrow Shuffle (or Bro. Hamman's, or a strip-out shuffle) · Card control · Pass

PERFORMANCE
- The shuffle has to look fair. Practise the cover mechanics until you'd believe it yourself.
- Build the "everything is hopelessly mixed" moment before the reveal.
- A signature on the card makes the reveal personal.
""",

    "Out of This World": """\
EFFECT
The spectator separates a shuffled deck into reds and blacks while looking only at the backs — and gets every single card right.

METHOD (Paul Curry, 1942)
The deck is pre-arranged: reds on top, blacks on the bottom (or vice versa). One marker red and one marker black on the table.

WORKING
1. False shuffle to keep the order.
2. Place a red card face-up at the left, black face-up at the right.
3. Spectator deals one card at a time from the top, choosing red pile or black.
   Because the top half is all reds, every card they deal lands in the red pile correctly.
4. After ~12 cards, casually say "let's switch — deal black with your right now."
   At this point you switch the marker cards (or rotate the layout) so the
   black-half cards land on the (now-black) right marker correctly.
5. Continue to the end.
6. Turn over the dealt piles — every card is correct.

CORE MOVES
False shuffle (a Charlier or any top-stock retainer) · the marker switch
(the version with two extra Jokers or pull-down works smoothly).

PERFORMANCE
- The "let's switch hands" moment must feel offhand. Don't draw attention to it.
- Pick a confident spectator — sells the impossibility.
- Resist the urge to peek. The deck does the work.
""",

    "Invisible Deck": """\
EFFECT
A spectator names any card. You produce a deck. Every card is face-up except theirs, which is reversed in the middle of the pack.

METHOD
Uses a "Brainwave" or Invisible-Deck gaff (rough-smooth pairs glued back-to-back). Self-working once the deck is set.

WORKING
1. Frame the effect as imagination: "I have an invisible deck. Pick any card,
   note it, slide it back into the imaginary deck and flip it over."
2. They name the card.
3. Reach into your pocket, "this is the deck I was thinking of."
4. Open the case and let the deck sit on the table for a beat — the named card is reversed inside.
5. Ribbon spread: every card face-up except theirs, face-down in the middle.
6. Pull it out and turn it over to confirm.

NOTES
- Practise the spread — uneven pressure breaks the rough-smooth pairs.
- Frame it as mentalism, not a deck switch.
- The first card and last card of the spread should be different, so it
  doesn't matter which way the deck is oriented when you open it.
""",

    "Card Warp": """\
EFFECT
A face-down card is folded around a face-up card. As it slides through the fold, the inner card visibly turns face-down — paradoxically.

METHOD
Roy Walton, 1974. No sleights. The illusion is geometric.

SETUP
Take two cards. Fold each in half along the LONG axis (creasing in opposite
directions). Place the face-up card inside the fold of the face-down card so they nest.

WORKING
1. Show both cards normally if you have time.
2. Make the fold and nest them.
3. SLOWLY slide the inner card across the outer fold. Half of the inner card
   visibly flips orientation as it crosses the crease line.
4. Continue the slide — the whole card appears to have turned face-down through the wrap.
5. Pull both cards apart — both look unfolded and normal.

PERFORMANCE
- Slow is more impossible than fast. Let the audience watch it happen.
- Watch their eyes — when the look of confusion hits, that's your moment.
- The unfolded "everything's normal" reset is the cherry on top.
""",

    "Oil and Water": """\
EFFECT
Three red cards and three black cards are alternately mixed together, then separate themselves into two groups again.

METHOD
Many variants. Common Vernon and Marlo handlings use specific counts.

BASIC WORKING (one common method)
1. Display six cards: R B R B R B (alternating).
2. Use an Elmsley Count to display them as still alternating while secretly
   swapping the order — they're now actually in two groups.
3. Spread or deal: the three reds are together, the three blacks are together.
4. Rebuild the alternation (sometimes via a Jordan Count) and repeat with a different convincer.
5. Final phase: deal them face-down, snap, turn over — completely separated.

CORE MOVES
Elmsley Count · Jordan Count · Block Push-off · Buckle Count

PERFORMANCE
- The fairer the apparent mixing looks, the stronger the separation feels.
- Three phases is the standard structure: convince, surprise, then kicker.
""",

    "Chicago Opener": """\
EFFECT
A red-backed card is selected and lost. It transforms in the spectator's hand and is the only blue-backed card in the deck.

METHOD (Frank Garcia / Al Leech "Red Hot Mama")
Uses a one-way force deck (or a single odd-back card).

WORKING
1. Spread a red-backed deck, force the only odd card (a specific card with a blue back).
2. Spectator looks at the face: it's, say, the four of clubs.
3. Spectator places the card face-down on the table or in their hand.
4. You riffle the deck and ask them to name their card.
5. Turn over their tabled card — it now has a BLUE back.
6. Spread the deck to show it's the only blue-backed card in a pack of reds.

CORE MOVES
Hindu Force / Classic Force (any reliable force) · turnover handling.

PERFORMANCE
- This is a perfect opener — fast, visual, no setup mid-routine.
- Patter is short. Let the colour change land cold.
""",

    "Do As I Do": """\
EFFECT
Two decks are used. You and the spectator each shuffle, cut, and select a card. When revealed, you've both picked the same card.

METHOD
Several variants — most common uses a glimpsed card.

BASIC WORKING
1. Use two regular decks. Spectator shuffles theirs, you shuffle yours.
2. Trade decks. Both cut, both select a card from the centre.
3. Glimpse the bottom card of your deck (now in the spectator's hands originally).
4. Trade decks back. Place selections on top, cut.
5. Look through your deck "to find your card" — find the glimpsed one and place it face-down.
6. Spectator does the same with their selection.
7. Both turn over — same card.

CORE MOVES
Glimpse (bottom-card glimpse during the cut). Optional false shuffle to retain the glimpse.

PERFORMANCE
- Build the patter around "do exactly what I do, every step."
- The glimpse is your only secret move — make it during a natural moment.
""",

    "Think of a Card": """\
EFFECT
The spectator merely thinks of a card. You divine it.

METHOD
Endless variants. Common ones use a peek, a one-ahead, equivoque, or a force-and-fish.

ONE WORKING (Riffle Force + Eyeball)
1. Riffle the deck. Spectator says "stop." Hold a break.
2. They take and remember the card you've forced.
3. Squared deck. You ask them to think hard.
4. Riffle the deck. Glimpse the force card during the riffle (or pre-glimpsed).
5. Slowly reveal — letter by letter, suit, value, climaxing with the name.

CORE MOVES
Force · Glimpse · Cold reading patter

PERFORMANCE
- Slow reveals build tension. Don't blurt the answer.
- Read their face and pace your reveals.
- A wrong-then-right structure ("...oh, no — a HEART!") is more dramatic than going straight to the answer.
""",

    "The Biddle Trick": """\
EFFECT
Spectator selects a card, returns it to the deck. You count five cards into your hand — their card has vanished from the count and reappears in the deck (or they hold it themselves).

METHOD
Uses the Biddle Steal / Biddle Count — Elmer Biddle, 1947.

WORKING
1. Force or freely select a card. Spectator notes and replaces it on top.
2. Cut to bury it in the middle.
3. Take five cards face-up off the top one at a time, biddle-style (right hand
   peels each onto the previous).
4. As you take the last card, secretly steal the spectator's card back into your right hand.
5. Place the five-card packet down.
6. Have spectator name their card. Count the packet — only four cards.
7. Reveal the missing card on top of the deck (or in spectator's pocket).

CORE MOVES
Biddle Steal · Card control · Force (optional)

PERFORMANCE
- The biddle take must look like a genuine "I'm just showing you each card" action.
- Don't telegraph the steal — keep your tempo steady throughout the count.
""",

    "Princess Card Trick": """\
EFFECT
Five cards are shown. Spectator mentally chooses one. You display the cards again — their chosen card is gone.

METHOD
The "ghost card" trick — uses two sets of five completely different cards. No selection is actually tracked; ANY card they think of will be removed.

WORKING
1. Display five cards (e.g. AS, 5H, 7D, KC, 9C). "Think of one."
2. Square the packet, snap, "I'll remove your card."
3. Display five DIFFERENT cards (e.g. 3S, 8H, JD, 6C, 2C).
4. Their card is "missing" — but really, EVERY card is missing because all five are different.

PRO TIP
Modern handlings use a double-faced or rough-smooth card, or simply swap the packet under cover (lap, pocket, or a switch on the move).

PERFORMANCE
- Don't repeat — once is enough. Repeat performance gives the secret away.
- Keep eye contact. The trick is the patter as much as the move.
""",

    "Lie Detector": """\
EFFECT
A spectator picks a card and replies to your questions either truthfully or with lies. By tracking their answers, you find the card.

METHOD
A spelling / counting force, or a "magician's choice" combined with deck arrangement.

ONE WORKING
1. Spectator picks a card from the top half of the deck.
2. You ask: "Is your card red?" — they answer truthfully or with a lie. Repeat for suit, value range, etc.
3. Each answer corresponds to dealing one card off the top OR keeping it.
   The total number of "yes" answers (or the spelling of "yes" and "no") leads you to the card.
4. Reveal the card at the position determined by their answers.

CORE MOVES
Card control · Counting / spelling routine

PERFORMANCE
- Make the spectator commit to either honesty or lying for the whole routine — variety kills the maths.
- The patter of catching them lying is half the entertainment.
""",

    "Mental Photography": """\
EFFECT
The deck is shown to be entirely blank. You make a "mental photograph" — the deck is now a regular printed pack. Magic happens again — back to blank.

METHOD
The Brainwave/Mental Photo gaff deck (alternating blank-faced and printed cards, or rough-smooth pairs).

WORKING
1. Spread the deck face-up: every card appears blank.
2. Square up. Wave. Riffle the corners — visual "printing" effect.
3. Spread again: every card is now a regular printed card.
4. Repeat to vanish the printing back to blank.

CORE
The deck does the work — the magic is in the spread (uneven pressure shows
all of one face, even pressure shows the other).

PERFORMANCE
- Practise the spread until it's bulletproof. A misfired spread shows the
  wrong faces and kills the trick.
- The riffle "printing" sound effect amps up the visual.
""",

    "Four Ace Trick": """\
EFFECT
The four Aces are placed in four different positions in the deck, yet they all assemble into one pile.

METHOD
Many variations (Vernon's "Slow Motion Four Aces", Marlo's, etc.). Common base method uses three indifferent cards on top of a leader Ace.

ONE WORKING (Slow Motion)
1. Set up: from top, three indifferent cards then the four Aces (or one Ace
   on top with three indifferents above it, depending on method).
2. Display four Aces, deal them face-down on the table at four corners.
3. On three of them, secretly add three indifferent cards (Vernon's add-on).
4. Each pile has one "Ace" on top. Three indifferent cards underneath.
5. Snap. Turn over the pile in the corner — all four Aces have travelled there.

CORE MOVES
Vernon's Slip Cut Add-On · Top Change · Double Lift

PERFORMANCE
- The deal at the corners must look casual.
- Each Ace placement is a beat. Don't rush.
""",

    "Acrobatic Aces": """\
EFFECT
Four Aces visually jump from one position to another, one at a time.

METHOD
Uses the Atomic Aces principle, Marlo's Acrobatic Aces, or a similar add-on/swap.

GENERAL STRUCTURE
1. Display the four Aces in a row.
2. Phase one: top Ace vanishes from one packet and reappears in another.
3. Phase two: another Ace travels.
4. Phase three: third travels.
5. Climax: all Aces in one pile, the others empty (or replaced with another suit).

CORE MOVES
Elmsley Count · Slip Cut · Add-on · Top Change

PERFORMANCE
- Phases of three to four work best. More than that and the audience loses count.
""",

    "Spectator Cuts to the Aces": """\
EFFECT
Spectator cuts the deck into four piles. They turn over the top of each pile — every one is an Ace.

METHOD
Cross-cut / multiple-cut deception. Aces start on top; the cuts only appear to randomise.

WORKING
1. Set up: four Aces on top of the deck.
2. False shuffle (top-stock retainer).
3. Cut the deck into four roughly equal piles, left to right. Note which pile contains the original top.
4. Have the spectator perform a sequence of cuts that appears to mix but actually
   transfers the four top cards (the Aces) onto each of the four piles. The
   classic handling: cut three from the original top pile and put one on each
   other pile, then cut three from another pile to itself. The Aces end up on top.
5. Turn over the top card of each pile — Ace, Ace, Ace, Ace.

CORE MOVES
False shuffle · The "cut, count three, cut" routine.

PERFORMANCE
- This is a TIMING piece. Keep the rhythm of the cuts steady and the maths is invisible.
- A confident spectator sells the cleanness.
""",

    "Twisted Aces": """\
EFFECT
The four Aces are shown all face-down. Each turns face-up, one at a time, while the others stay face-down — until all four are face-up.

METHOD
Dai Vernon's "Twisting the Aces" using the Elmsley Count.

WORKING
1. Hold four Aces face-down.
2. Snap the packet. Elmsley Count to show three face-down and one face-up (the second Ace).
3. Adjust the order. Snap. Elmsley to show the next.
4. Repeat for the third.
5. Final: spread to show all four face-up.

CORE MOVES
Elmsley Count · Through-the-fist flourish for the "twisting" visual

PERFORMANCE
- Each "twist" is a beat. Hold for a moment so the audience registers it.
- The final spread is the kicker — let it land.
""",

    "Any Card at Any Number (ACAAN)": """\
EFFECT
Spectator names ANY card. Another spectator names ANY number 1–52. You count down to that number — there's their card.

METHOD
The Berglas Effect is the holy grail. Practical methods include:
- Stacked deck (Mnemonica / Aronson) + cut
- Cross-cut force + miscounted deal
- Multiple outs (a card at one position from top, one from bottom, one in the case)
- Card index in pocket

ONE WORKING (Mnemonica)
1. Deck in Mnemonica order. False shuffle.
2. Spectator names a card. You know its position N in the stack.
3. Spectator names a number M.
4. If N = M: deal. Done.
5. Otherwise: cut at position (N − M). Now their card is at position M from the top.
6. Deal down to M. Reveal.

CORE MOVES
False shuffle · Stack memorisation · Cuts

PERFORMANCE
- The naming has to feel completely free. Practise the cut handling so the maths is invisible.
- Pace the deal. Let the count build tension.
""",

    "21 Card Trick": """\
EFFECT
Spectator picks one of 21 cards by thinking of it. After three deals into three rows, you know their card.

METHOD
Self-working classic. Pure maths.

WORKING
1. Deal 21 cards face-up into three columns of seven, dealing left-to-right
   one card at a time.
2. Spectator points at the column containing their card.
3. Pick up the cards: their column goes IN THE MIDDLE.
4. Re-deal into three columns. Ask which column.
5. Their column goes in the middle again.
6. Re-deal once more. Ask. Their column in the middle.
7. After the third deal, their card is the 11th card (middle of 21).

CORE MOVES
None. Pure deal mechanics.

PERFORMANCE
- This is a beginner's trick. Dress it up with patter to disguise the maths.
- The reveal at the end can be the 11th card OR a "spelling" reveal off the middle of the dealt rows.
""",

    "Card to Wallet": """\
EFFECT
Selected card vanishes from the deck and reappears in your wallet — sometimes inside a sealed compartment.

METHOD
Requires a special wallet (Mullica, Kaps, Himber, Plus Wallet, Z-fold). The wallet does the load.

GENERAL WORKING
1. Selection by force or free choice.
2. Card controlled to a palm position.
3. Deck set down. Reach for wallet.
4. Load the palmed card into the wallet's secret compartment as you remove it.
5. Spectator opens the wallet — card inside.

CORE MOVES
Card palm (Top, Tenkai, or Side Steal palm) · Loading move

PERFORMANCE
- The wallet must come out cleanly without fumbling — practise the load until it's invisible.
- Use a real wallet you'd carry every day. A "magic wallet" looks like a magic wallet.
- Selection signed = strongest version. The signed card in your sealed wallet is unbeatable.
""",

    "Card to Pocket": """\
EFFECT
Selected card vanishes from the deck and reappears in your pocket.

METHOD
Card palm + load to pocket.

WORKING
1. Selection. Control to top of deck.
2. Top palm into right hand.
3. Place deck in left hand or table. Right hand into right pocket.
4. Drop palmed card in pocket. Or load into a hidden clip.
5. Have spectator name card. Riffle the deck — gone.
6. Reach into pocket, produce the card.

CORE MOVES
Top Palm · Card control · Misdirection (the reach to pocket itself is the cover)

PERFORMANCE
- The reach to the pocket should look casual. Don't telegraph the load.
- Practise palming until you can hold the card with a relaxed hand.
""",

    "Card Under Glass": """\
EFFECT
Selected card vanishes from the deck. The drinking glass is lifted — the card is underneath.

METHOD
Side steal or top palm + load under glass.

WORKING
1. Selection, controlled to top.
2. Use a glass on the table (set up earlier). Top palm in right hand.
3. As you reach to "make sure the glass is steady," load the palmed card under the glass.
4. Riffle the deck — card is gone.
5. Spectator lifts the glass — there it is.

CORE MOVES
Top Palm or Side Steal · Loading under a tabled object

PERFORMANCE
- The load happens on misdirection. The audience must be looking at the deck or the spectator.
- Practise on a flat surface. The card must lie flat under the glass.
""",

    "The Rising Card": """\
EFFECT
Selected cards rise out of the deck on their own.

METHODS
Many: thread, sleights, gimmicked deck, plunger principle. The most elegant is sleight-only.

ONE WORKING (Sleight-Only)
1. Selection, controlled to second from top.
2. Hold the deck upright in left hand, faces toward spectator.
3. Right hand makes magic gesture. Behind the deck, the right pinkie pushes
   the back card up using a "plunger" action — but the card facing the
   spectator is the second card, not the top.
4. Card visibly rises. Spectator names it. It's the same one.

CORE MOVES
Card control · The Plunger move (pinkie behind deck)

PERFORMANCE
- Angle is critical. Audience must be in front, not to the side.
- Slow rises are more magical than fast.
""",

    "Three Card Monte": """\
EFFECT
A street-game-style routine. Spectator tries to follow the queen (or whatever marked card) — and is wrong every time.

METHOD
Mexican Turnover, Monte Move, throw with a hidden swap.

WORKING
1. Three cards: two indifferent and one queen.
2. Display all three. Throw to the table — the queen "is in the middle."
3. Spectator points to the queen. You turn it over — it's not the queen.
4. Repeat with twists: tabled queen has changed cards, etc.
5. Climax: all three cards turn out to be queens, or the queen has vanished entirely.

CORE MOVES
Mexican Turnover · Monte Throw · Block Switch

PERFORMANCE
- The Monte is about RHYTHM. The throw must look natural.
- Patter as a hustle: "find the lady..." but make sure the audience knows it's a magic trick, not a con.
- Build to a kicker the spectator can't predict.
""",

    "Sam the Bellhop": """\
EFFECT
A long story about Sam the bellhop visiting a hotel. As you tell it, the cards
deal out in perfect order to match every plot beat.

METHOD
Frank Everhart / Bill Malone. The deck is in a specific stack. Each phase of
the story matches a position in the stack. False shuffles preserve the stack
between phases.

STRUCTURE
1. Set up the deck. Practise false shuffles that retain order.
2. Begin the story: "Sam the bellhop walked into the hotel..."
3. As you describe each character, deal the matching card off the top.
4. Phases include: cards in royal flush order, suits separating, etc.
5. Final phase: every card lands in a perfect ordered display.

CORE MOVES
False shuffle (a strong overhand or riffle-stack retainer) · Memorised story

PERFORMANCE
- This is a STORY trick. The story is the trick — practise the patter as much as the deals.
- Don't break character to focus on the cards. The narrative carries them.
- Best with a relaxed casual audience, not a busy table.
""",

    "Pick a Card (basic)": """\
EFFECT
The classic. Spectator picks any card, returns it, you find it.

METHOD
Pick any control + reveal you like. Good for working out moves.

BASIC WORKING
1. Spread for selection. Spectator removes a card, notes it.
2. Square the deck. Spectator returns the card to the middle.
3. Control to top via Pass, Hindu Shuffle Control, or Overhand Control.
4. Reveal: top card with a flourish, or build into one of the bigger effects below.

CORE MOVES
Any control: Hindu Control · Overhand Control · Classic Pass · Cut Control

PERFORMANCE
- This is the MOTHER of all tricks. Use it as a foundation for showing off a specific control.
- Never just say "is this your card?" — make the reveal entertaining.
""",

    "The 10-20 Trick": """\
EFFECT
Spectator silently chooses a number between 10 and 20. After a sequence of
deals and reverses, the chosen card always ends up at a specific position.

METHOD
Pure self-working maths. The 10-20 force.

WORKING
1. Spread cards face-up. Spectator silently picks a number N between 10 and 20.
2. Deal N cards into a face-down pile. The pile reverses the order.
3. Add the digits of N (e.g. 14 → 1+4 = 5). Deal that many cards back onto the deck.
4. The spectator's card is now at position 9 from the top of the dealt pile.
5. Reveal.

CORE
None. Pure number mechanics.

PERFORMANCE
- The maths is invisible to the spectator if you keep tempo.
- Build the tension on the reveal — don't telegraph that you know.
""",

    "The Self-Working Card Trick": """\
EFFECT
Various — the term is generic. Tricks that require no sleights, just procedure.

EXAMPLES
- 10-20 Force (above)
- 21 Card Trick (above)
- Australian Deal (count down, deal alternately, reveal)
- Spelling tricks (deal one card per letter of card name)
- The Reversed Card prediction

GENERAL APPROACH
1. Choose a procedure-driven trick that fits the moment.
2. Set up the patter so the procedure feels meaningful, not arbitrary.
3. Reveal cleanly.

PERFORMANCE NOTES FOR SELF-WORKERS
- Self-working ≠ trivial. The patter is your art form.
- Don't expose the procedure as "maths." Frame it as ritual or chance.
- The best magicians have one or two killer self-workers in their pocket.
""",
}
