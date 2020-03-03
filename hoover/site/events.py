from django.conf import settings

if settings.HOOVER_EVENTS_DIR:
    from time import time
    from datetime import datetime
    import json
    from pathlib import Path
    from django.dispatch import receiver
    from ..contrib import installed
    from ..search import signals as search_signals

    root = Path(settings.HOOVER_EVENTS_DIR)

    if not root.exists():
        root.mkdir(parents=True)

    def save(**data):
        t = time()
        data['time'] = t
        day = datetime.utcfromtimestamp(t).date()
        logfile = root / (day.isoformat() + '.txt')
        with logfile.open('ab') as f:
            f.write(json.dumps(data).encode('utf-8') + b'\n')

    @receiver(search_signals.search)
    def on_search(sender, request, collections, duration, success, **kw):
        save(
            type='search',
            username=request.user.get_username(),
            collections=[c.name for c in collections],
            duration=duration,
            success=success,
        )

    @receiver(search_signals.doc)
    def on_doc(sender, request, collection, duration, success, **kw):
        save(
            type='document',
            username=request.user.get_username(),
            collections=[collection.name],
            duration=duration,
            success=success,
        )

    @receiver(search_signals.batch)
    def on_batch(sender, request, collections, duration, success, query_count, **kw):
        save(
            type='batch',
            username=request.user.get_username(),
            collections=[c.name for c in collections],
            duration=duration,
            success=success,
            query_count=query_count,
        )

    @receiver(search_signals.rate_limit_exceeded)
    def on_search_rate_limit_exceeded(sender, username, **kw):
        save(type='rateLimitExceeded', username=username)

    if installed.twofactor:
        from django.contrib.auth import signals as auth_signals
        from ..contrib.twofactor import signals as twofactor_signals

        @receiver(auth_signals.user_logged_in)
        def on_login(sender, user, **kw):
            save(type='login', username=user.get_username())

        @receiver(twofactor_signals.invitation_create)
        def on_invitation_create(sender, username, operator, **kw):
            save(type='invitationCreate', username=username, operator=operator)

        @receiver(twofactor_signals.invitation_open)
        def on_invitation_open(sender, username, **kw):
            save(type='invitationOpen', username=username)

        @receiver(twofactor_signals.invitation_accept)
        def on_invitation_accept(sender, username, **kw):
            save(type='invitationAccept', username=username)

        @receiver(twofactor_signals.invitation_expired)
        def on_invitation_expired(sender, username, **kw):
            save(type='invitationExpired', username=username)

        @receiver(twofactor_signals.auto_logout)
        def on_auto_logout(sender, username, **kw):
            save(type='forceLogout', username=username)

        @receiver(twofactor_signals.login_failure)
        def on_login_failure(sender, otp_failure, **kw):
            save(type='loginFailed', otp_failure=otp_failure)

        @receiver(twofactor_signals.rate_limit_exceeded)
        def on_otp_rate_limit_exceeded(sender, username, **kw):
            save(type='otpRateLimitExceeded', username=username)
