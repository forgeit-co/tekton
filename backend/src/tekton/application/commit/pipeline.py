from tekton.application.shared.protocols import CommitCapability, Committer, WriteSession


class CommitPipeline(Committer):
    def commit(self, session: WriteSession, commit_capability: CommitCapability) -> None:
        """TODO(§5.6): append events and revalidate before committing the UoW."""
        session.collect_events()
        commit_capability.commit()
