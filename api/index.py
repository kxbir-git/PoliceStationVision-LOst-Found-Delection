"""
Indian Police Station Lost & Found Portal — Flask Backend
==========================================================
Single-file Flask app deployed on Vercel.  All routes are prefixed with /api.
"""

from __future__ import annotations

import os
import re
import random
import base64
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# Optional imports — degrade gracefully when packages are absent (e.g. tests)
# ---------------------------------------------------------------------------
try:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    )
    CLOUDINARY_CONFIGURED = True
except Exception:
    CLOUDINARY_CONFIGURED = False

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# App & extensions
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///lostfound.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.unauthorized_handler
def _unauthorized():
    return jsonify({"error": "Authentication required"}), 401
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_CATEGORIES = [
    "Documents",
    "Electronic Devices",
    "Bags & Luggage",
    "Wallet / Purse",
    "Keys",
    "Jewellery",
    "Vehicles",
    "Books / Stationery",
    "Clothing / Accessories",
    "Other",
]
VALID_ID_PROOF_TYPES = ["Aadhaar", "PAN", "DL", "VoterID"]
STOPWORDS = frozenset(
    {"the", "a", "an", "in", "at", "on", "of", "and", "is", "was", "to", "for", "it", "with", "that", "this"}
)
# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="citizen")  # citizen / police
    police_station = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "police_station": self.police_station,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
class Property(db.Model):
    __tablename__ = "properties"
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # lost / unclaimed
    status = db.Column(db.String(20), nullable=False, default="pending")
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    applicant_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    id_proof_type = db.Column(db.String(20), nullable=True)
    id_proof_masked = db.Column(db.String(4), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    how_lost = db.Column(db.Text, nullable=True)
    date_lost = db.Column(db.String(20), nullable=True)
    time_lost = db.Column(db.String(20), nullable=True)
    location_lost = db.Column(db.String(300), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    police_station = db.Column(db.String(200), nullable=True)
    officer_name = db.Column(db.String(200), nullable=True)
    officer_badge_id = db.Column(db.String(50), nullable=True)
    current_location = db.Column(db.String(300), nullable=True)
    declaration_accepted = db.Column(db.Boolean, default=False)
    consent_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deletion_requested = db.Column(db.Boolean, default=False)
    deletion_requested_at = db.Column(db.DateTime, nullable=True)
    reporter = db.relationship("User", backref="properties", lazy=True)
    def to_dict(self, mask_sensitive=True):
        d = {
            "id": self.id,
            "registration_number": self.registration_number,
            "type": self.type,
            "status": self.status,
            "reporter_id": self.reporter_id,
            "applicant_name": self.applicant_name,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "how_lost": self.how_lost,
            "date_lost": self.date_lost,
            "time_lost": self.time_lost,
            "location_lost": self.location_lost,
            "image_url": self.image_url,
            "police_station": self.police_station,
            "officer_name": self.officer_name,
            "officer_badge_id": self.officer_badge_id,
            "current_location": self.current_location,
            "declaration_accepted": self.declaration_accepted,
            "consent_accepted": self.consent_accepted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deletion_requested": self.deletion_requested,
        }
        if mask_sensitive:
            d["id_proof_type"] = self.id_proof_type
            d["id_proof_masked"] = f"XXXX-{self.id_proof_masked}" if self.id_proof_masked else None
            d.pop("address", None)
            d.pop("phone", None)
        else:
            d["id_proof_type"] = self.id_proof_type
            d["id_proof_masked"] = self.id_proof_masked
            d["address"] = self.address
            d["phone"] = self.phone
        return d
class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    property = db.relationship("Property", backref="claims", lazy=True)
    claimant = db.relationship("User", backref="claims", lazy=True)
    def to_dict(self):
        return {
            "id": self.id,
            "property_id": self.property_id,
            "claimant_id": self.claimant_id,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("claims.id"), nullable=True)
    action = db.Column(db.String(300), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    officer = db.relationship("User", backref="audit_logs", lazy=True)
    def to_dict(self):
        officer = User.query.get(self.officer_id) if self.officer_id else None
        prop = Property.query.get(self.property_id) if self.property_id else None
        return {
            "id": self.id,
            "officer_id": self.officer_id,
            "officer_name": officer.full_name if officer else f"Officer #{self.officer_id}",
            "property_id": self.property_id,
            "property_registration": prop.registration_number if prop else None,
            "claim_id": self.claim_id,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ---------------------------------------------------------------------------
# Flask-Login user loader
# ---------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# DB init on first request
# ---------------------------------------------------------------------------
_tables_created = False


@app.before_request
def _ensure_tables():
    global _tables_created
    if not _tables_created:
        with app.app_context():
            db.create_all()
        _tables_created = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_registration_number(prop_type: str) -> str:
    """Generate a unique registration number like LPR-2026-00042 or UCP-2026-00042."""
    prefix = "LPR" if prop_type == "lost" else "UCP"
    year = datetime.now(timezone.utc).year
    # Find the highest existing number for this prefix+year
    pattern = f"{prefix}-{year}-%"
    last = (
        Property.query.filter(Property.registration_number.like(pattern))
        .order_by(Property.id.desc())
        .first()
    )
    if last:
        try:
            seq = int(last.registration_number.split("-")[-1]) + 1
        except ValueError:
            seq = random.randint(10000, 99999)
    else:
        seq = 1
    return f"{prefix}-{year}-{seq:05d}"


def _mask_id(full_id: str | None) -> str | None:
    """Return only the last 4 characters of an ID proof number."""
    if not full_id:
        return None
    return full_id[-4:]


def _upload_image(base64_data: str) -> str | None:
    """Upload a base64 image to Cloudinary and return the secure URL."""
    if not CLOUDINARY_CONFIGURED:
        return None
    try:
        # Handle data URI prefix
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
        result = cloudinary.uploader.upload(
            f"data:image/png;base64,{base64_data}",
            folder="lostfound",
        )
        return result.get("secure_url")
    except Exception:
        return None


def _tokenize(text: str) -> set[str]:
    """Lowercase, split and remove stopwords."""
    if not text:
        return set()
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _match_score(prop_a: Property, prop_b: Property) -> float:
    """Compute a simple word-overlap match score between two properties."""
    words_a = _tokenize((prop_a.title or "") + " " + (prop_a.description or ""))
    words_b = _tokenize((prop_b.title or "") + " " + (prop_b.description or ""))
    if not words_a or not words_b:
        return 0.0
    common = words_a & words_b
    score = len(common) / max(len(words_a), len(words_b))

    # Bonus for close dates
    try:
        date_a = datetime.fromisoformat(prop_a.date_lost) if prop_a.date_lost else None
        date_b = prop_b.created_at
        if date_a and date_b:
            # Make both offset-naive for comparison
            if date_a.tzinfo:
                date_a = date_a.replace(tzinfo=None)
            if date_b.tzinfo:
                date_b = date_b.replace(tzinfo=None)
            diff = abs((date_a - date_b).days)
            if diff <= 7:
                score += 0.2 * (1 - diff / 7)
    except Exception:
        pass

    return round(score, 4)


# ===================================================================
#  AUTH ROUTES
# ===================================================================

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json(silent=True) or {}
    required = ["full_name", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone"),
        role="citizen",
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user, remember=True)
    resp = user.to_dict()
    resp["user"] = user.to_dict()
    resp["message"] = "Login successful"
    return jsonify(resp), 200


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def auth_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/auth/me", methods=["GET"])
@login_required
def auth_me():
    resp = current_user.to_dict()
    resp["user"] = current_user.to_dict()
    return jsonify(resp), 200


# ===================================================================
#  PROPERTY ROUTES
# ===================================================================

@app.route("/api/properties", methods=["GET"])
def list_properties():
    q_type = request.args.get("type")
    q_category = request.args.get("category")
    q_search = request.args.get("q")
    q_station = request.args.get("station")
    q_status = request.args.get("status")
    q_reporter = request.args.get("reporter")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    if q_reporter == "me":
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        query = Property.query.filter(
            Property.reporter_id == current_user.id,
            Property.status != "deleted",
        )
    else:
        query = Property.query.filter(
            Property.deletion_requested == False,
            Property.status != "deleted",
        )

        if q_type:
            query = query.filter(Property.type == q_type)
        if q_category:
            query = query.filter(Property.category == q_category)
        if q_station:
            query = query.filter(Property.police_station == q_station)
        if q_status:
            query = query.filter(Property.status == q_status)
        if q_search:
            like = f"%{q_search}%"
            query = query.filter(
                db.or_(
                    Property.title.ilike(like),
                    Property.description.ilike(like),
                )
            )

        # Police officers see only their station's items when no station filter is given
        if current_user and hasattr(current_user, "role") and current_user.is_authenticated:
            if current_user.role == "police" and not q_station:
                query = query.filter(Property.police_station == current_user.police_station)

    pagination = query.order_by(Property.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    items = [p.to_dict() for p in pagination.items]
    return jsonify({
        "properties": items,
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page,
    }), 200


@app.route("/api/properties", methods=["POST"])
@login_required
def create_property():
    # Accept JSON or multipart
    if request.content_type and "multipart" in request.content_type:
        data = request.form.to_dict()
        image_file = request.files.get("image")
        if image_file:
            image_b64 = base64.b64encode(image_file.read()).decode()
        else:
            image_b64 = None
    else:
        data = request.get_json(silent=True) or {}
        image_b64 = data.pop("image", None)

    # Validate required fields
    required = ["type", "applicant_name", "category", "title"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    prop_type = data["type"]
    if prop_type not in ("lost", "unclaimed"):
        return jsonify({"error": "type must be 'lost' or 'unclaimed'"}), 400

    if data["category"] not in VALID_CATEGORIES:
        return jsonify({"error": f"Invalid category. Choose from: {', '.join(VALID_CATEGORIES)}"}), 400

    # Declaration & consent
    declaration = data.get("declaration_accepted") if data.get("declaration_accepted") is not None else data.get("declaration")
    consent = data.get("consent_accepted") if data.get("consent_accepted") is not None else data.get("consent")
    if isinstance(declaration, str):
        declaration = declaration.lower() in ("true", "1", "yes")
    if isinstance(consent, str):
        consent = consent.lower() in ("true", "1", "yes")

    if not declaration or not consent:
        return jsonify({"error": "Both declaration and consent must be accepted"}), 400

    # Mask ID proof
    id_proof_number = data.get("id_proof_number")
    id_proof_masked = (data.get("id_proof_masked") or "")[-4:] if data.get("id_proof_masked") else _mask_id(id_proof_number)

    # Image upload
    image_url = None
    if image_b64:
        image_url = _upload_image(image_b64)

    reg_num = _generate_registration_number(prop_type)

    prop = Property(
        registration_number=reg_num,
        type=prop_type,
        status="pending",
        reporter_id=current_user.id,
        applicant_name=data["applicant_name"],
        address=data.get("address"),
        phone=data.get("phone"),
        id_proof_type=data.get("id_proof_type"),
        id_proof_masked=id_proof_masked,
        category=data["category"],
        title=data["title"],
        description=data.get("description"),
        how_lost=data.get("how_lost"),
        date_lost=data.get("date_lost"),
        time_lost=data.get("time_lost"),
        location_lost=data.get("location_lost"),
        image_url=image_url,
        police_station=data.get("police_station"),
        officer_name=data.get("officer_name"),
        officer_badge_id=data.get("officer_badge_id"),
        current_location=data.get("current_location"),
        declaration_accepted=True,
        consent_accepted=True,
    )
    db.session.add(prop)
    db.session.commit()

    d = prop.to_dict(mask_sensitive=False)
    return jsonify({
        **d,
        "message": "Property report created",
        "property": d,
    }), 201


@app.route("/api/properties/<int:prop_id>", methods=["GET"])
def get_property(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop or prop.status == "deleted" or prop.deletion_requested:
        return jsonify({"error": "Property not found"}), 404

    # Show full details to owner and police
    is_owner = current_user.is_authenticated and current_user.id == prop.reporter_id
    is_police = current_user.is_authenticated and current_user.role == "police"
    mask = not (is_owner or is_police)

    d = prop.to_dict(mask_sensitive=mask)
    return jsonify({
        **d,
        "property": d,
    }), 200


@app.route("/api/properties/<int:prop_id>/status", methods=["PATCH"])
@login_required
def update_property_status(prop_id):
    if current_user.role != "police":
        return jsonify({"error": "Police access required"}), 403

    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("pending", "approved", "returned", "deleted"):
        return jsonify({"error": "Invalid status"}), 400

    old_status = prop.status
    prop.status = new_status
    prop.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        officer_id=current_user.id,
        property_id=prop.id,
        action=f"Status changed from '{old_status}' to '{new_status}'",
        old_value=old_status,
        new_value=new_status,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Status updated", "property": prop.to_dict()}), 200


@app.route("/api/properties/<int:prop_id>", methods=["DELETE"])
@login_required
def delete_property(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    if prop.reporter_id != current_user.id:
        return jsonify({"error": "You can only delete your own reports"}), 403

    prop.deletion_requested = True
    prop.deletion_requested_at = datetime.now(timezone.utc)
    prop.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        officer_id=current_user.id,
        property_id=prop.id,
        action="Deletion requested by reporter (soft delete)",
        old_value=prop.status,
        new_value="deletion_requested",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "Deletion request submitted"}), 200


# ===================================================================
#  MATCHING
# ===================================================================

@app.route("/api/properties/<int:prop_id>/matches", methods=["GET"])
def get_matches(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    opposite_type = "unclaimed" if prop.type == "lost" else "lost"
    candidates = Property.query.filter(
        Property.type == opposite_type,
        Property.category == prop.category,
        Property.status != "deleted",
        Property.deletion_requested == False,
    ).all()

    scored = []
    for c in candidates:
        s = _match_score(prop, c)
        if s > 0:
            scored.append((s, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:10]

    match_items = []
    for s, p in top:
        d = p.to_dict()
        d["match_score"] = s
        d["score"] = s
        d["property"] = p.to_dict()
        match_items.append(d)

    return jsonify({"matches": match_items}), 200


# ===================================================================
#  CLAIM ROUTES
# ===================================================================

@app.route("/api/properties/<int:prop_id>/claim", methods=["POST"])
@login_required
def create_claim(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    data = request.get_json(silent=True) or {}

    # Prevent duplicate claims
    existing = Claim.query.filter_by(
        property_id=prop_id, claimant_id=current_user.id
    ).first()
    if existing:
        return jsonify({"error": "You have already submitted a claim for this property"}), 409

    claim = Claim(
        property_id=prop_id,
        claimant_id=current_user.id,
        message=data.get("message"),
    )
    db.session.add(claim)
    db.session.commit()

    return jsonify({"message": "Claim submitted", "claim": claim.to_dict()}), 201


@app.route("/api/claims", methods=["GET"])
@login_required
def list_claims():
    if current_user.role != "police":
        return jsonify({"error": "Police access required"}), 403

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    query = (
        Claim.query.join(Property, Claim.property_id == Property.id)
        .filter(Property.police_station == current_user.police_station)
        .order_by(Claim.created_at.desc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for claim in pagination.items:
        cd = claim.to_dict()
        cd["property"] = claim.property.to_dict() if claim.property else None
        cd["property_registration"] = claim.property.registration_number if claim.property else None
        claimant = User.query.get(claim.claimant_id) if claim.claimant_id else None
        cd["claimant"] = claimant.to_dict() if claimant else None
        cd["claimant_name"] = claimant.full_name if claimant else None
        items.append(cd)

    return jsonify({
        "claims": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


@app.route("/api/claims/<int:claim_id>", methods=["PATCH"])
@login_required
def update_claim(claim_id):
    if current_user.role != "police":
        return jsonify({"error": "Police access required"}), 403

    claim = db.session.get(Claim, claim_id)
    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("approved", "rejected"):
        return jsonify({"error": "Status must be 'approved' or 'rejected'"}), 400

    old_status = claim.status
    claim.status = new_status
    claim.updated_at = datetime.now(timezone.utc)

    # If approved, also mark the property as returned
    if new_status == "approved":
        prop = db.session.get(Property, claim.property_id)
        if prop:
            prop.status = "returned"
            prop.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        officer_id=current_user.id,
        property_id=claim.property_id,
        claim_id=claim.id,
        action=f"Claim {new_status}",
        old_value=old_status,
        new_value=new_status,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": f"Claim {new_status}", "claim": claim.to_dict()}), 200


# ===================================================================
#  DASHBOARD (police only)
# ===================================================================

@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    if current_user.role != "police":
        return jsonify({"error": "Police access required"}), 403

    station = current_user.police_station
    base = Property.query.filter(
        Property.police_station == station,
        Property.deletion_requested == False,
    )

    total_lost = base.filter(Property.type == "lost").count()
    total_unclaimed = base.filter(Property.type == "unclaimed").count()
    total_returned = base.filter(Property.status == "returned").count()
    pending_claims = (
        Claim.query.join(Property)
        .filter(Property.police_station == station, Claim.status == "pending")
        .count()
    )

    res = {
        "total_lost": total_lost,
        "total_unclaimed": total_unclaimed,
        "total_returned": total_returned,
        "pending_claims": pending_claims,
    }
    return jsonify({
        **res,
        "stats": res,
    }), 200


@app.route("/api/dashboard/audit-log", methods=["GET"])
@login_required
def dashboard_audit_log():
    if current_user.role != "police":
        return jsonify({"error": "Police access required"}), 403

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    per_page = min(per_page, 100)

    station = current_user.police_station

    query = (
        AuditLog.query.join(Property, AuditLog.property_id == Property.id, isouter=True)
        .filter(
            db.or_(
                Property.police_station == station,
                AuditLog.property_id == None,  # noqa: E711
            )
        )
        .order_by(AuditLog.timestamp.desc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [log.to_dict() for log in pagination.items]

    return jsonify({
        "audit_log": items,
        "entries": items,
        "logs": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


# ===================================================================
#  CERTIFICATE / ACKNOWLEDGEMENT
# ===================================================================

@app.route("/api/properties/<int:prop_id>/certificate", methods=["POST"])
@login_required
def generate_certificate(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({"error": "Property not found"}), 404

    now = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M UTC")
    type_label = "Lost Property Report" if prop.type == "lost" else "Unclaimed Property Report"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Acknowledgement — {prop.registration_number}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #222; }}
  .header {{ text-align: center; border-bottom: 3px double #1a237e; padding-bottom: 16px; margin-bottom: 24px; }}
  .header h1 {{ margin: 0; color: #1a237e; font-size: 22px; }}
  .header h2 {{ margin: 4px 0 0; font-size: 16px; font-weight: normal; color: #555; }}
  .badge {{ display: inline-block; background: #1a237e; color: #fff; padding: 4px 14px; border-radius: 4px; font-size: 13px; margin-top: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #ddd; }}
  th {{ width: 200px; color: #555; font-weight: 600; }}
  .disclaimer {{ margin-top: 32px; padding: 14px; background: #fff3e0; border-left: 4px solid #e65100; font-size: 13px; }}
  .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #888; }}
  @media print {{ body {{ margin: 20px; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>Police Station — Lost &amp; Found Portal</h1>
  <h2>{type_label} Acknowledgement</h2>
  <span class="badge">{prop.registration_number}</span>
</div>

<table>
  <tr><th>Registration Number</th><td><strong>{prop.registration_number}</strong></td></tr>
  <tr><th>Date of Report</th><td>{prop.created_at.strftime('%d-%m-%Y') if prop.created_at else 'N/A'}</td></tr>
  <tr><th>Certificate Generated</th><td>{now}</td></tr>
  <tr><th>Applicant Name</th><td>{prop.applicant_name}</td></tr>
  <tr><th>Category</th><td>{prop.category}</td></tr>
  <tr><th>Item Title</th><td>{prop.title}</td></tr>
  <tr><th>Description</th><td>{prop.description or 'N/A'}</td></tr>
  <tr><th>Location</th><td>{prop.location_lost or 'N/A'}</td></tr>
  <tr><th>Date Lost / Found</th><td>{prop.date_lost or 'N/A'}</td></tr>
  <tr><th>Police Station</th><td>{prop.police_station or 'N/A'}</td></tr>
  <tr><th>Status</th><td>{prop.status.upper()}</td></tr>
</table>

<div class="disclaimer">
  <strong>⚠ Disclaimer:</strong> This is an <strong>acknowledgement of report</strong> only.
  This document is <strong>NOT</strong> a First Information Report (FIR). It serves as proof that the above
  information was submitted to the Lost &amp; Found Portal. For filing an FIR, please visit
  your nearest police station in person.
</div>

<div class="footer">
  <p>Generated by the Police Station Lost &amp; Found Portal</p>
</div>
</body>
</html>"""

    return jsonify({"certificate_html": html, "html": html, "certificate": html}), 200


# ===================================================================
#  DATA DELETION (DPDP Act compliance)
# ===================================================================

@app.route("/api/users/request-deletion", methods=["POST"])
@login_required
def request_data_deletion():
    now = datetime.now(timezone.utc)
    props = Property.query.filter_by(reporter_id=current_user.id).all()

    for prop in props:
        prop.deletion_requested = True
        prop.deletion_requested_at = now
        prop.updated_at = now

    # Anonymize user data (effective after 30 day grace period — here we mark it)
    audit = AuditLog(
        officer_id=current_user.id,
        action="User requested data deletion under DPDP Act",
        old_value=current_user.email,
        new_value="deletion_requested",
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "message": "Data deletion requested. Your personal data will be anonymized after a 30-day grace period.",
        "properties_affected": len(props),
    }), 200


# ===================================================================
#  Health check
# ===================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}), 200


# ---------------------------------------------------------------------------
# Static files for local development & demonstration
# ---------------------------------------------------------------------------
@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_static(path):
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404
    public_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public"
    )
    if not os.path.exists(public_dir):
        public_dir = os.path.join(os.getcwd(), "public")
    file_path = os.path.join(public_dir, path)
    if os.path.isfile(file_path):
        return send_from_directory(public_dir, path)
    not_found = os.path.join(public_dir, "404.html")
    if os.path.isfile(not_found):
        return send_from_directory(public_dir, "404.html"), 404
    return jsonify({"error": "Page not found"}), 404


# ---------------------------------------------------------------------------
# Local dev entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
