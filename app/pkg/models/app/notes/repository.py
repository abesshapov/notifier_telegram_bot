"""Note repository models."""

from app.pkg.models.app.notes import NoteFields


class CreateNoteCommand(NoteFields.Text, NoteFields.ReminderTime, NoteFields.UserId):
    """Create Note command."""


class ReadNoteQueryById(NoteFields.Identifiers):
    """Read Note query."""


class ReadNotesQueryByUserId(NoteFields.UserId):
    """Read Notes for user by id."""


class NoteResponse(
    NoteFields.Identifiers,
    NoteFields.UserId,
    NoteFields.Text,
    NoteFields.ReminderTime,
):
    """Note response."""


class UpdateNoteNotifiedStateCommand(
    NoteFields.Identifiers,
    NoteFields.Notified,
):
    """Update note notified state command."""


class DeleteNoteCommand(NoteFields.Identifiers):
    """Delete Note command."""
