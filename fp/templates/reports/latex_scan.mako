\begin{table}[t]
\caption{Sample table title}
\label{sample-table}
\begin{center}
\begin{tabular}{rrrrrrr}
&
\multicolumn{1}{r}{\bf Regions} &
\multicolumn{1}{r}{\bf Windows} &
\multicolumn{1}{r}{\bf Windows} &
\multicolumn{1}{r}{\bf Windows} &
& <%text>\\
</%text> \

&
\multicolumn{1}{r}{\bf below} &
\multicolumn{1}{r}{\bf percent} &
\multicolumn{1}{r}{\bf false} &
\multicolumn{1}{r}{\bf false} &
\multicolumn{1}{r}{\bf Scan} &
\multicolumn{1}{r}{\bf Train} <%text>\\
</%text> \

\multicolumn{1}{r}{\bf Name} &
\multicolumn{1}{r}{\bf 95\%} &
\multicolumn{1}{r}{\bf error} &
\multicolumn{1}{r}{\bf positive} &
\multicolumn{1}{r}{\bf negative} &
\multicolumn{1}{r}{\bf time} &
\multicolumn{1}{r}{\bf time} <%text>\\
\hline \\
</%text> \

% for preparedResult in sorted(preparedResults, key=lambda x: x['patch_percentError']):
${'%50s' % preparedResult['resultName']} & \
% if preparedResult['patch_percentError'] != None:
${'%5.1f \%%' % float(preparedResult['patch_percentError'])} 
% endif
& \
${'%5.1f \%%' % float(preparedResult['scan_percentError'])} & \
${'%5.1f \%%' % float(preparedResult['scan_falsePositiveError'])} & \
${'%5.1f \%%' % float(preparedResult['scan_falseNegativeError'])} & \
% if preparedResult['scan_elapsedTimeInMinutes'] != 0:
${'%5.1f hrs' % (float(preparedResult['scan_elapsedTimeInMinutes']) / 60)} \
% else:
        - \
% endif
& \
${'%5.1f hrs' % (float(preparedResult['classifier_elapsedTimeInMinutes']) / 60)} <%text>\\</%text>
% endfor
\end{tabular}
\end{center}
\end{table}
