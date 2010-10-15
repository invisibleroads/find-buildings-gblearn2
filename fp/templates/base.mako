## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
<link rel="shortcut icon" href="/files/favicon.ico" />
${h.javascript_link('/files/jquery-1.3.2.min.js')}
${h.stylesheet_link('/files/style.css')}
<title>${h.SITE_NAME} ${self.title()}</title>
<style>${self.css()}</style>
${self.head()}
<script>
    $(document).ready(function() {
        $('input').addClass('normalFONT');
        $('textarea').addClass('normalFONT');
        $('select').addClass('normalFONT');
        $('a').hover(
            function () {this.className = this.className.replace('OFF', 'ON');}, 
            function () {this.className = this.className.replace('ON', 'OFF');}
        );
        $('.tabOFF').hover(
            function() {this.className = this.className.replace('OFF', 'ON');}, 
            function() {this.className = this.className.replace('ON', 'OFF');} 
        ).click(function() {$('#' + this.id + '_').toggle();}); 
        // $('.tab_').hide(); 
        $('#help_button').click(function () {$('.help').toggle();});
        $('#browse').change(function() {
            window.location = this.value;
        });
        ${self.js()}
    });
</script>
</head>
<body class=normalFONT>
    <div id=header>
        <div id=toolbar>${self.toolbar()}</div>
        <div id=navigation>
            ${self.navigation()}
        % if not h.isPerson():
        % if not request.path.startswith('/people/login'):
            <a id=person_login href="${h.url_for('person_login', url=h.encodeURL(request.path))}" class=linkOFF>Login</a>
        % endif
        % else:
            <a id=person_update href="${h.url_for('person_update')}" class=linkOFF>${session['nickname']}</a>
            &nbsp;
            <a id=person_logout href="${h.url_for('person_logout', url=h.encodeURL(request.path))}" class=linkOFF>Logout</a>
        % endif
        </div>
    </div>
    <div id=main>
        ${next.body()}
    </div>
    <div id=footer>
        <div id=board>${self.board()}</div>
        <div id=support>
            ${self.support()}
            &nbsp;
            <select id=browse>
                <option>Browse</option>
            % for browseName in 'image', 'region', 'window', 'dataset', 'classifier', 'scan', 'location':
            <%
                browseURL = h.url_for(browseName + '_index')
                browseTitle = browseName.title() + 's'
            %>
                <option value="${browseURL}" \
                % if browseURL == request.path:
                    selected\
                % endif
                >${browseTitle}</option>
            % endfor
            </select>
            &nbsp;
        % if request.path != h.url_for('index'):
            <a id=index href="${h.url_for('index')}" class=linkOFF>Index</a>
            &nbsp;
        % endif
            <a id=help_button class=linkOFF>Help</a>
        </div>
    </div>
</body>
</html>

<%def name="title()"></%def>
<%def name="css()"></%def>
<%def name="head()"></%def>
<%def name="js()"></%def>
<%def name="toolbar()"></%def>
<%def name="navigation()"></%def>
<%def name="board()"></%def>
<%def name="support()"></%def>
