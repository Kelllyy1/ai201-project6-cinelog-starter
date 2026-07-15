import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    AlreadyInWatchlistError,
    NotInWatchlistError
)
from services.collection_service import FilmNotFoundError

@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="watcher", email="watch@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        # Note: Film.id is a UUID string following the rebase on main
        film = Film(title="Inception", year=2010, genre="Sci-Fi")
        db.session.add(film)
        db.session.commit()
        return film.id

# ── Comment 3: Nonexistent Film Test ─────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Comment 3 Fix: Adding a film_id that doesn't exist should raise
    FilmNotFoundError, matching the pattern in test_collection.py.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)

# ── Comment 2: Deduplication Test ────────────────────────────────────────────

def test_add_to_watchlist_deduplication(app, sample_user, sample_film):
    """
    Comment 2 Fix: Adding the same film twice should raise AlreadyInWatchlistError.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        # Confirm only one entry exists in the database
        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1

# ── Stretch Feature: Removal Functionality ───────────────────────────────────

def test_remove_from_watchlist_stretch(app, sample_user, sample_film):
    """
    Stretch Feature: Verifies removing an item deletes it from the database.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)
        
        # Act
        result = remove_from_watchlist(user_id=sample_user, film_id=sample_film)
        assert result is True
        
        # Assert database state
        remain = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert remain is None

# ── Stretch Feature: Edge Case ───────────────────────────────────────────────

def test_remove_nonexistent_watchlist_raises(app, sample_user, sample_film):
    """
    Stretch Feature Edge Case: Trying to remove an item that isn't on the
    watchlist should raise a NotInWatchlistError.
    """
    with app.app_context():
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)
