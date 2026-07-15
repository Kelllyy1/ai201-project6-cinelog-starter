"""
services/watchlist_service.py — CineLog

Business logic for the watchlist feature.
"""
from app import db
from models import Film, WatchlistEntry
from services.collection_service import FilmNotFoundError

class AlreadyInWatchlistError(Exception):
    """Raised when a film is already in the user's watchlist."""
    pass

class NotInWatchlistError(Exception):
    """Raised when trying to remove a film that isn't in the watchlist."""
    pass

def add_to_watchlist(user_id, film_id, public=True):
    """
    Add a film to a user's watchlist (saved for later).

    Args:
        user_id (str): UUID of the user.
        film_id (str): UUID of the film (Updated from int for Milestone 3 UUID migration).
        public (bool, optional): Visibility status. Defaults to True.
    
    Comment 1 Fixed: Renamed from save_to_watchlist to match verb_to_noun.
    Stretch Feature Fixed: Added 'public' visibility parameter.
    """
    film = db.session.get(Film, film_id)
    if film is None:
        raise FilmNotFoundError(f"No film found with id '{film_id}'")

    # Comment 2 Fixed: Service-level check prevents duplicate entries
    existing = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    if existing:
        raise AlreadyInWatchlistError(
            f"Film '{film_id}' is already on this user's watchlist"
        )

    entry = WatchlistEntry(user_id=user_id, film_id=film_id, public=public)
    db.session.add(entry)
    db.session.commit()
    return entry

def remove_from_watchlist(user_id, film_id):
    """
    STRETCH FEATURE: Implement remove_from_watchlist function.
    """
    entry = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    if entry is None:
        raise NotInWatchlistError(
            f"Film '{film_id}' is not on this user's watchlist"
        )

    db.session.delete(entry)
    db.session.commit()
    return True

def get_watchlist(user_id):
    """
    Comment 5 Fixed: Default watchlists to 'date added' descending order
    instead of sorting alphabetically by Film.title.
    """
    entries = (
        WatchlistEntry.query
        .filter_by(user_id=user_id)
        .order_by(WatchlistEntry.date_added.desc())
        .all()
    )

    result = []
    for entry in entries:
        film_dict = entry.film.to_dict()
        film_dict["date_added"] = entry.date_added.isoformat()
        film_dict["public"] = entry.public
        result.append(film_dict)

    return result
