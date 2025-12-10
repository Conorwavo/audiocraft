"""Artist profile MVP demo.

This script builds a universal artist profile schema that can be consumed
by multiple agents (production, marketing, splits, contracting, distribution).
It combines public information, user-supplied goals, and private DAW-style
integrations into a single data model. The output includes both a human-friendly
markdown view and machine-readable JSON/JSON-LD structures.

Run the script directly to see example output:
    python demos/artist_profile_mvp.py
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Dict, List
import json


@dataclass
class PublicPresence:
    stage_name: str
    legal_name: str
    primary_genres: List[str]
    hometown: str
    biography: str
    social_links: Dict[str, str]
    streaming_metrics: Dict[str, Dict[str, int]]
    notable_releases: List[Dict[str, str]]


@dataclass
class UserIntent:
    creative_goals: List[str]
    brand_voice: str
    target_audience: List[str]
    milestones: List[str]
    collaboration_preferences: List[str]


@dataclass
class DAWSession:
    daw: str
    project_name: str
    file_path: str
    tempo_bpm: float
    key_signature: str
    stems_available: bool
    last_touched: date


@dataclass
class RightsSplit:
    role: str
    contributor: str
    percentage: float


@dataclass
class PrivateIntegrations:
    daw_sessions: List[DAWSession]
    rights_splits: List[RightsSplit]
    management_contacts: Dict[str, str]
    preferred_distributors: List[str]
    contract_terms: Dict[str, str]


@dataclass
class ArtistProfile:
    public_presence: PublicPresence
    user_intent: UserIntent
    private_integrations: PrivateIntegrations
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        """Return the unified profile as a plain dictionary."""
        return asdict(self)

    def jsonld(self) -> Dict[str, object]:
        """Return a JSON-LD representation suitable for knowledge graphs."""
        base = {
            "@context": {
                "name": "http://schema.org/name",
                "Person": "http://schema.org/Person",
                "MusicGroup": "http://schema.org/MusicGroup",
                "memberOf": "http://schema.org/memberOf",
                "genre": "http://schema.org/genre",
                "knowsAbout": "http://schema.org/knowsAbout",
                "sameAs": "http://schema.org/sameAs",
                "CreativeWork": "http://schema.org/CreativeWork",
                "Distribution": "https://schema.org/Organization",
            },
            "@type": "Person",
            "name": self.public_presence.stage_name,
            "alternateName": self.public_presence.legal_name,
            "genre": self.public_presence.primary_genres,
            "homeLocation": self.public_presence.hometown,
            "description": self.public_presence.biography,
            "sameAs": list(self.public_presence.social_links.values()),
            "knowsAbout": self.tags,
            "hasPart": [
                {
                    "@type": "CreativeWork",
                    "name": release.get("title"),
                    "datePublished": release.get("release_date"),
                    "inLanguage": release.get("language", "en"),
                    "genre": release.get("genre"),
                }
                for release in self.public_presence.notable_releases
            ],
        }

        return base

    def agent_view(self, agent: str) -> Dict[str, object]:
        """Return a tailored view of the profile for a specific agent type."""
        agent = agent.lower()
        if agent == "production":
            return self._production_view()
        if agent == "marketing":
            return self._marketing_view()
        if agent == "splits":
            return self._splits_view()
        if agent == "contracting":
            return self._contract_view()
        if agent == "distribution":
            return self._distribution_view()
        raise ValueError(f"Unknown agent view: {agent}")

    def _production_view(self) -> Dict[str, object]:
        sessions = []
        for session in self.private_integrations.daw_sessions:
            serialized = asdict(session)
            serialized["last_touched"] = session.last_touched.isoformat()
            sessions.append(serialized)
        return {
            "stage_name": self.public_presence.stage_name,
            "genres": self.public_presence.primary_genres,
            "creative_goals": self.user_intent.creative_goals,
            "daw_sessions": sessions,
        }

    def _marketing_view(self) -> Dict[str, object]:
        return {
            "stage_name": self.public_presence.stage_name,
            "bio": self.public_presence.biography,
            "audience": self.user_intent.target_audience,
            "social_links": self.public_presence.social_links,
            "streaming_metrics": self.public_presence.streaming_metrics,
            "milestones": self.user_intent.milestones,
        }

    def _splits_view(self) -> Dict[str, object]:
        return {
            "stage_name": self.public_presence.stage_name,
            "rights": [asdict(split) for split in self.private_integrations.rights_splits],
            "management_contacts": self.private_integrations.management_contacts,
        }

    def _contract_view(self) -> Dict[str, object]:
        return {
            "legal_name": self.public_presence.legal_name,
            "stage_name": self.public_presence.stage_name,
            "contract_terms": self.private_integrations.contract_terms,
            "management_contacts": self.private_integrations.management_contacts,
        }

    def _distribution_view(self) -> Dict[str, object]:
        return {
            "stage_name": self.public_presence.stage_name,
            "preferred_distributors": self.private_integrations.preferred_distributors,
            "notable_releases": self.public_presence.notable_releases,
            "streaming_metrics": self.public_presence.streaming_metrics,
        }

    def to_markdown(self) -> str:
        """Return a human-friendly, visually rich markdown representation."""
        releases = "\n".join(
            f"- **{release['title']}** ({release['release_date']}) — {release['genre']}"
            for release in self.public_presence.notable_releases
        )
        sessions = "\n".join(
            f"- `{session.daw}` session **{session.project_name}** at {session.tempo_bpm} BPM in {session.key_signature}"
            for session in self.private_integrations.daw_sessions
        )
        rights = "\n".join(
            f"- {split.contributor} — {split.role}: {split.percentage:.1f}%"
            for split in self.private_integrations.rights_splits
        )
        social = " ".join(f"[{name}]({url})" for name, url in self.public_presence.social_links.items())

        return f"""
# 🎨 {self.public_presence.stage_name}

## Identity & Story
- Legal: **{self.public_presence.legal_name}**
- Genres: {', '.join(self.public_presence.primary_genres)}
- Hometown: {self.public_presence.hometown}
- Bio: {self.public_presence.biography}
- Links: {social}

## Vision
- Goals: {', '.join(self.user_intent.creative_goals)}
- Voice: _{self.user_intent.brand_voice}_
- Audience: {', '.join(self.user_intent.target_audience)}
- Milestones: {', '.join(self.user_intent.milestones)}
- Collab prefs: {', '.join(self.user_intent.collaboration_preferences)}

## Catalogue & Sessions
{releases}

### DAW Sessions
{sessions}

## Rights & Business
### Splits
{rights}

### Contracts & Distribution
- Preferred distributors: {', '.join(self.private_integrations.preferred_distributors)}
- Contract terms: {json.dumps(self.private_integrations.contract_terms, indent=2)}
"""


def demo_profile() -> ArtistProfile:
    """Build a sample artist profile with multi-agent semantics."""
    public_presence = PublicPresence(
        stage_name="Lumen Echo",
        legal_name="Avery Calder",
        primary_genres=["electronic", "indie pop"],
        hometown="Berlin, DE",
        biography="Cinematic electronic producer blending modular textures with pop sensibilities.",
        social_links={
            "instagram": "https://instagram.com/lumen.echo",
            "spotify": "https://open.spotify.com/artist/lumenecho",
            "youtube": "https://youtube.com/@lumenecho",
        },
        streaming_metrics={
            "spotify": {"monthly_listeners": 125000, "playlist_adds": 4200},
            "youtube": {"subscribers": 18400, "views_30d": 210000},
        },
        notable_releases=[
            {"title": "Neon Veins", "release_date": "2023-08-18", "genre": "electronic"},
            {"title": "Glass Gardens", "release_date": "2022-11-05", "genre": "indie pop"},
        ],
    )

    user_intent = UserIntent(
        creative_goals=["Write a cinematic EP", "Expand live show"],
        brand_voice="Futuristic, cinematic, empathetic",
        target_audience=["festival goers", "sci-fi film fans"],
        milestones=["Lock EP tracklist", "Book spring tour", "Secure sync placements"],
        collaboration_preferences=["female vocalists", "analog synth engineers"],
    )

    private_integrations = PrivateIntegrations(
        daw_sessions=[
            DAWSession(
                daw="Ableton Live",
                project_name="Neon Veins Lead",
                file_path="/Volumes/Projects/LumenEcho/neon_veins.als",
                tempo_bpm=118.0,
                key_signature="F# minor",
                stems_available=True,
                last_touched=date(2024, 12, 3),
            ),
            DAWSession(
                daw="Logic Pro",
                project_name="Glass Gardens Remix",
                file_path="/Volumes/Projects/LumenEcho/glass_gardens.logicx",
                tempo_bpm=102.0,
                key_signature="C major",
                stems_available=False,
                last_touched=date(2024, 10, 11),
            ),
        ],
        rights_splits=[
            RightsSplit(role="Composer", contributor="Avery Calder", percentage=65.0),
            RightsSplit(role="Producer", contributor="Nova Grey", percentage=25.0),
            RightsSplit(role="Mixer", contributor="Skyline Studio", percentage=10.0),
        ],
        management_contacts={"manager": "manager@lumenecho.com", "legal": "legal@lumenecho.com"},
        preferred_distributors=["DistroKid", "Stem"],
        contract_terms={"master": "Artist owned", "publishing": "Admin deal", "term": "2 years"},
    )

    return ArtistProfile(
        public_presence=public_presence,
        user_intent=user_intent,
        private_integrations=private_integrations,
        tags=["producer", "songwriter", "live performer"],
    )


def main() -> None:
    profile = demo_profile()
    print("\n===== HUMAN VIEW (Markdown) =====\n")
    print(profile.to_markdown())

    print("\n===== JSON-LD =====\n")
    print(json.dumps(profile.jsonld(), indent=2))

    print("\n===== AGENT VIEWS =====\n")
    for view in ["production", "marketing", "splits", "contracting", "distribution"]:
        print(f"-- {view.upper()} --")
        print(json.dumps(profile.agent_view(view), indent=2))


if __name__ == "__main__":
    main()
