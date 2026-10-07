from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app import db, limiter
from app.models import User
from app.security import log_security_event
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import io
import base64


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def home():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if not user:

            log_security_event(
                "LOGIN_FAILURE",
                username=username
            )

            flash("Invalid username or password.")

            return redirect(url_for("main.home"))

        # Check whether the account is locked
        if user.account_locked:

            flash(
                "Your account is locked. Please contact an administrator."
            )

            return redirect(url_for("main.home"))

        # Verify the password against the stored hash
        if not check_password_hash(user.password_hash, password):

            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:

                user.account_locked = True

                db.session.commit()

                log_security_event(
                    "ACCOUNT_LOCKED",
                    username=username,
                    details="5 failed login attempts"
                )

                flash(
                    "Your account has been locked after too many failed login attempts."
                )

                return redirect(url_for("main.home"))

            db.session.commit()

            log_security_event(
                "LOGIN_FAILURE",
                username=username
            )

            flash("Invalid username or password.")

            return redirect(url_for("main.home"))

        # Successful password authentication
        user.failed_login_attempts = 0

        db.session.commit()

        log_security_event(
            "PASSWORD_AUTH_SUCCESS",
            username=username
        )

        # Check whether MFA is enabled
        if user.mfa_enabled:

            # Store the user temporarily while MFA is pending
            session["mfa_user_id"] = user.id

            return redirect(url_for("main.mfa_verify"))

        # MFA is not enabled
        session["user_id"] = user.id
        session["username"] = user.username
        session["mfa_verified"] = False

        flash("Password authentication successful.")

        return redirect(url_for("main.dashboard"))

    return render_template("login.html")

@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("main.register"))

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("main.register"))

        password_hash = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. You can now sign in.")

        return redirect(url_for("main.home"))

    return render_template("register.html")
     
@main.route("/mfa/setup", methods=["GET", "POST"])
def mfa_setup():

    if "user_id" not in session:
        flash("Please sign in to set up MFA.")
        return redirect(url_for("main.home"))

    user = User.query.get(session["user_id"])

    # Generate MFA secret if one does not exist
    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        db.session.commit()

    # Handle MFA verification
    if request.method == "POST":

        verification_code = request.form.get(
            "verification_code",
            ""
        ).strip()

        totp = pyotp.TOTP(user.mfa_secret)

        if totp.verify(verification_code):

            user.mfa_enabled = True
            db.session.commit()

            flash("MFA has been successfully enabled.")

            return redirect(url_for("main.dashboard"))

        flash("Invalid MFA verification code.")

    # Create TOTP provisioning URI
    totp = pyotp.TOTP(user.mfa_secret)

    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="SecureAuth"
    )

    # Generate QR code
    qr = qrcode.make(provisioning_uri)

    # Store QR code in memory
    img_buffer = io.BytesIO()
    qr.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Convert QR code to Base64
    qr_code = base64.b64encode(
        img_buffer.getvalue()
    ).decode("utf-8")

    return f"""
        <h1>MFA Setup</h1>

        <p>Scan the QR code using your authenticator app.</p>

        <img
            src="data:image/png;base64,{qr_code}"
            alt="MFA QR Code"
        >

        <p>
            <strong>Account:</strong> {user.email}
        </p>

        <p>
            Enter the 6-digit code generated by your
            authenticator app:
        </p>

        <form method="POST">

            <input
                type="text"
                name="verification_code"
                placeholder="Enter 6-digit code"
                maxlength="6"
                required
            >

            <button type="submit">
                Verify & Enable MFA
            </button>

        </form>
    """

@main.route("/mfa/verify", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def mfa_verify():

    if "mfa_user_id" not in session:
        flash("Please sign in first.")
        return redirect(url_for("main.home"))

    user = User.query.get(session["mfa_user_id"])

    if not user or not user.mfa_enabled:
        flash("MFA verification is not required.")
        return redirect(url_for("main.home"))

    if request.method == "POST":

        verification_code = request.form.get(
            "verification_code",
            ""
        ).strip()

        if not verification_code.isdigit() or len(verification_code) != 6:

            flash("Please enter a valid 6-digit MFA code.")

            return redirect(url_for("main.mfa_verify"))

        totp = pyotp.TOTP(user.mfa_secret)

        is_valid = totp.verify(verification_code)

        if is_valid:

            # MFA successfully completed
            session.pop("mfa_user_id", None)

            session["user_id"] = user.id
            session["username"] = user.username
            session["mfa_verified"] = True

            log_security_event(
                "MFA_SUCCESS",
                username=user.username
            )

            flash("MFA verification successful.")

            return redirect(url_for("main.dashboard"))

        else:

         print("MFA FAILURE BRANCH REACHED")

        log_security_event(
        "MFA_FAILURE",
        username=user.username
        )
        
        flash("Invalid MFA verification code.")

    return render_template("mfa_verify.html")

@main.route("/dashboard")
def dashboard():

    # No authentication at all
    if "user_id" not in session:

        # Check whether the user has passed password authentication
        # but has not completed MFA
        if "mfa_user_id" in session:

            user = User.query.get(session["mfa_user_id"])

            if user:

                log_security_event(
                    "UNAUTHORIZED_ACCESS",
                    username=user.username,
                    details="Attempted access to /dashboard before MFA verification"
                )

            session.clear()

            flash("MFA verification is required.")

            return redirect(url_for("main.home"))

        # Completely unauthenticated request
        log_security_event(
            "UNAUTHORIZED_ACCESS",
            details="Attempted access to /dashboard without authentication"
        )

        flash("Please sign in to access the dashboard.")

        return redirect(url_for("main.home"))

    user = User.query.get(session["user_id"])

    if user and user.mfa_enabled:

        if not session.get("mfa_verified", False):

            log_security_event(
                "UNAUTHORIZED_ACCESS",
                username=user.username,
                details="Attempted access to /dashboard before MFA verification"
            )

            session.clear()

            flash("MFA verification is required.")

            return redirect(url_for("main.home"))

    return f"""
        <h1>Welcome, {session["username"]}!</h1>

        <p>Password authentication successful.</p>

        <p>MFA verification completed.</p>

        <a href="{url_for("main.logout")}">
            Log out
        </a>
    """
@main.route("/logout")
def logout():

    username = session.get("username")

    log_security_event(
        "LOGOUT",
        username=username
    )

    session.clear()

    return redirect(url_for("main.home"))