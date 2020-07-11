from authenticate import Auth


class Stats:
    """Get requested statistics of the user's activities."""
    def __init__(self):
        self.auth = Auth()

    def resolve_query(self, query):
        """Parse query and get corresponding stats."""
        pass
