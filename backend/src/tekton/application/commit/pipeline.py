from tekton.application.shared.protocols import Committer, WriteSession


class CommitPipeline(Committer):
    def commit(self, session: WriteSession) -> None:
        session.collect_events()
