import asyncio
from otree.api import Bot, Submission
from . import Instructions, Decision, Results, C


def _call(method, id_in_group, data):
    gen = method(id_in_group, data)
    # In oTree 6, method() returns an async generator
    if hasattr(gen, '__anext__'):
        async def _consume():
            res = None
            async for item in gen:
                res = item
            return res
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, _consume()).result()
            else:
                return loop.run_until_complete(_consume())
        except RuntimeError:
            return asyncio.run(_consume())
    return gen


def call_live_method(method, group, case, **kwargs):
    if case == 'with_bids':
        # Initial sync
        res = _call(method, 1, {'type': 'sync'})
        assert res == {1: {'highest_bid': C.STARTING_BID, 'highest_bidder': 0, 'leader': None}}

        # 1) Valid bid: Player 1 bids 20
        res = _call(method, 1, {'type': 'bid', 'bid': 20})
        assert res == {0: {'highest_bid': 20, 'highest_bidder': 1, 'leader': 'Player 1'}}
        assert group.highest_bid == 20
        assert group.highest_bidder == 1

        # 2) Equal bid: Player 2 bids 20 (invalid, must be strictly greater)
        res = _call(method, 2, {'type': 'bid', 'bid': 20})
        assert res == {2: {'error': 'Invalid bid'}}

        # 3) Above budget bid: Player 2 bids 81 (invalid, budget is 80)
        res = _call(method, 2, {'type': 'bid', 'bid': 81})
        assert res == {2: {'error': 'Invalid bid'}}

        # 4) Valid bid: Player 2 bids 35
        res = _call(method, 2, {'type': 'bid', 'bid': 35})
        assert res == {0: {'highest_bid': 35, 'highest_bidder': 2, 'leader': 'Player 2'}}
        assert group.highest_bid == 35
        assert group.highest_bidder == 2

    elif case == 'no_bids':
        # No bids placed, just sync
        res = _call(method, 1, {'type': 'sync'})
        assert res == {1: {'highest_bid': C.STARTING_BID, 'highest_bidder': 0, 'leader': None}}
        assert group.highest_bid == C.STARTING_BID
        assert group.highest_bidder == 0


class PlayerBot(Bot):
    cases = ['with_bids', 'no_bids']

    def play_round(self):
        yield Instructions
        # Bot times out on Decision page to simulate 60s timeout
        yield Submission(Decision, timeout_happened=True, check_html=False)

        # Assert payoffs
        if self.case == 'with_bids':
            if self.player.id_in_group == self.group.highest_bidder:
                expected_payoff = C.BUDGET - self.group.highest_bid + C.ITEM_VALUE
                assert self.player.payoff == expected_payoff, f"Winner payoff was {self.player.payoff}, expected {expected_payoff}"
            else:
                assert self.player.payoff == C.BUDGET, f"Non-winner payoff was {self.player.payoff}, expected {C.BUDGET}"
        elif self.case == 'no_bids':
            assert self.player.payoff == C.BUDGET, f"Payoff without bids was {self.player.payoff}, expected {C.BUDGET}"

        yield Results
