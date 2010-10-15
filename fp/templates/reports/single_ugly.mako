<%def name="unravel(data, level)">
% for key, value in data.iteritems():
    % if value != '' and value != [] and value != {}:
        % if isinstance(value, dict):
            <div class=indented>
                <h${level}>${key.title()}</h${level}>
                ${unravel(value, level + 1)}
            </div>
        % elif isinstance(value, list):
            <h${level}>${key.title()}</h${level}>
            <ol>
                % for item in value:
                <li>${unravel(item, level + 1)}</li>
                % endfor
            </ol>
        % else:
            ${key.title()} = ${value}<br>
        % endif
    % endif
% endfor
</%def>


<!doctype html>
<html>
<head>
<style>
.indented {
    margin-left: 2em;
}
</style>
</head>
<body>
% for key in 'patches', 'locations', 'scans', 'classifiers', 'datasets', 'sources':
    % if key in result:
        <% 
        value = result[key]
        %>
        % if value != {}:
            <h1>${key.title()}</h1>
            ${unravel(value, 2)}
        % endif
    % endif
% endfor
</body>
</html>
