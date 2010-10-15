We've received your ${c.action} request for the following credentials.

Username: ${c.username}
% if c.password:
Password: ${c.password}
% endif

Please click on the link below to complete your ${c.action}.
${request.relative_url(h.url_for('person_confirm', ticket=c.ticket), to_application=True)}

This ticket expires on ${c.when_expired.strftime('%A, %B %d, %Y at %H:%M%p')}.
