from otree.api import *

doc = """
Real-time English auction: 60 seconds, ascending bids, budget-constrained.
Winner pays their bid and receives the item value. Includes a built-in chat.
"""


class C(BaseConstants):
    NAME_IN_URL = 'live_auction'
    PLAYERS_PER_GROUP = 4      # 3 or 4
    NUM_ROUNDS = 1
    STARTING_BID = 10
    BUDGET = 80
    ITEM_VALUE = 100
    TIMEOUT_SECONDS = 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    highest_bid = models.IntegerField(initial=C.STARTING_BID)
    highest_bidder = models.IntegerField(initial=0)   # id_in_group, 0 = nobody yet


class Player(BasePlayer):
    pass


# ---------- helpers ----------
def auction_state(group: Group):
    """Payload sent to the clients."""
    return dict(
        highest_bid=group.highest_bid,
        highest_bidder=group.highest_bidder,
        leader=f"Player {group.highest_bidder}" if group.highest_bidder else None,
    )


# ---------- pages ----------
class Instructions(Page):
    pass


class StartWaitPage(WaitPage):
    """All members of the group start the auction together."""
    pass


class Decision(Page):
    timeout_seconds = C.TIMEOUT_SECONDS

    @staticmethod
    def js_vars(player: Player):
        return dict(
            my_id=player.id_in_group,
            budget=C.BUDGET,
            starting_bid=C.STARTING_BID,
        )

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        me = player.id_in_group

        # 1) Page just loaded: send the current state to this player only
        if isinstance(data, dict) and data.get('type') == 'sync':
            return {me: auction_state(group)}

        # 2) A bid
        try:
            bid = int(data.get('bid'))
        except (TypeError, ValueError, AttributeError):
            return {me: {'error': 'Invalid bid'}}

        if bid > group.highest_bid and bid <= C.BUDGET:
            group.highest_bid = bid
            group.highest_bidder = me
            return {0: auction_state(group)}          # broadcast to everyone

        return {me: {'error': 'Invalid bid'}}         # private error

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if player.id_in_group == group.highest_bidder:
            player.payoff = C.BUDGET - group.highest_bid + C.ITEM_VALUE
        else:
            player.payoff = C.BUDGET


class ResultsWaitPage(WaitPage):
    """Makes sure every player's before_next_page has run before Results is shown."""
    pass


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        has_winner = group.highest_bidder != 0
        rows = [
            dict(
                label=f"Player {p.id_in_group}",
                payoff=p.payoff,
                is_winner=(p.id_in_group == group.highest_bidder),
                is_me=(p.id_in_group == player.id_in_group),
            )
            for p in group.get_players()
        ]
        return dict(
            has_winner=has_winner,
            winner_label=f"Player {group.highest_bidder}",
            final_price=group.highest_bid,
            i_won=(player.id_in_group == group.highest_bidder),
            rows=rows,
        )


page_sequence = [Instructions, StartWaitPage, Decision, ResultsWaitPage, Results]
