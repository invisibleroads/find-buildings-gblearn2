<!doctype html>
<html>
<head>
<style>
body {
    font-family: Arial, Helvetica, sans-serif
}
table {
    border: medium solid black;
}
td {
    vertical-align: top;
    width: 7em;
    text-align: right;
}
td.long {width: 15em}
td.long_extra {width: 25em}
.indented {margin-left: 2em}
</style>
</head>
<body>


<%namespace name="s" file="shared.mako"/>
<% 
    import itertools 
    import numpy
%>


<h1>Summary</h1>
<div class=indented>
    <table>
        <%
            patchThresholds = []
            for result in results:
                patchInformation = result['patches']
                if patchInformation and 'performance by region' in patchInformation:
                    patchPerformance = patchInformation['performance']
                    patchParameters = patchInformation['patches']
                    patchThresholds.append(float(patchParameters['minimum percent correct']))
            patchMeanThreshold = numpy.mean(patchThresholds) if patchThresholds else None
        %>
        <tr>
            <td>Name</td>
            % if patchMeanThreshold:
            <td>Regions<br>below<br>${s.formatPercent(patchMeanThreshold)}</td>
            % endif
            <td>Locations<br>predicted not actual</td>
            <td>Locations<br>predicted</td>
            <td>Locations<br>PnA/P</td>
            <td>Locations<br>actual not predicted</td>
            <td>Locations<br>actual</td>
            <td>Locations<br>AnP/A</td>
            <td>Windows<br>percent error</td>
            <td>Windows<br>false positive</td>
            <td>Windows<br>false negative</td>
            <td>Scan time</td>
            <td>Train time</td>
        </tr>
        % for result in results:
        <%
            patchInformation = result['patches']
            if patchInformation and 'performance by region' in patchInformation:
                patchPerformance = patchInformation['performance']
                patchParameters = patchInformation['patches']
                patchPercentError = 1 - float(patchPerformance['percent correct'])
            else:
                patchPercentError = None
            if 'locations' in result:
                locationInformation = result['locations']
                locationPerformance = locationInformation['performance']
                actual = int(locationPerformance['actual count'])
                actualNotPredicted = int(locationPerformance['actual not predicted count'])
                predicted = int(locationPerformance['predicted count'])
                predictedNotActual = int(locationPerformance['predicted not actual count'])
            else:
                actual = None
                actualNotPredicted = None
                predicted = None
                predictedNotActual = None
            scanProbabilities = result['scans']['probabilities']
            scanProbabilitiesPerformance = scanProbabilities['performance']
            actualFalse_predictedTrue = scanProbabilitiesPerformance['actual false predicted true']
            actualFalse = scanProbabilitiesPerformance['actual false']
            actualTrue_predictedFalse = scanProbabilitiesPerformance['actual true predicted false']
            actualTrue = scanProbabilitiesPerformance['actual true']
            if 'elapsed time in seconds' in scanProbabilitiesPerformance:
                scanTime = '%0.1f min' % (float(scanProbabilitiesPerformance['elapsed time in seconds']) / 60)
            else:
                scanTime = ''
            classifierInformation = result['classifiers']
            classifierPerformance = classifierInformation['performance']
            if 'elapsed time in seconds' in classifierPerformance:
                trainTime = '%0.1f min' % (float(classifierPerformance['elapsed time in seconds']) / 60)
            else:
                trainTime = ''
        %>
        <tr>
            <td>${result['name']}</td>
            % if patchPercentError:
            <td>
                ${s.formatPercent(patchPercentError)}
            </td>
            % endif
            <td>${predictedNotActual}</td>
            <td>${predicted}</td>
            <td>
                % if predicted:
                ${s.formatPercent(predictedNotActual / float(predicted))}
                % endif
            </td>
            <td>${actualNotPredicted}</td>
            <td>${actual}</td>
            <td>
                % if actual:
                ${s.formatPercent(actualNotPredicted / float(actual))}
                % endif
            </td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['percent error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['false positive error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['false negative error'], fromDecimal=False)}</td>
            <td>${scanTime}</td>
            <td>${trainTime}</td>
        </tr>
        % endfor
    </table>
</div>


<h1>Patches</h1>
<div class=indented>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Region count</td>
            <td>Performance mean</td>
            <td>Performance standard deviation</td>
            <td>Performance threshold</td>
            <td>Bad region count</td>
            <td>Percent error over regions</td>
        </tr>
        % for result in results:
        <%
            patchInformation = result['patches']
            if patchInformation and 'performance by region' in patchInformation:
                patchPerformance = patchInformation['performance']
                patchPerformanceByRegion = patchInformation['performance by region']
                patchParameters = patchInformation['patches']
                patchRegionPerformances = [float(x) for x in patchPerformanceByRegion.values()]
            else:
                continue
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${patchPerformance['region count']}</td>
            <td>${s.formatPercent(numpy.mean(patchRegionPerformances))}</td>
            <td>${s.formatPercent(numpy.std(patchRegionPerformances))}</td>
            <td>${s.formatPercent(patchParameters['minimum percent correct'])}</td>
            <td>${patchPerformance['bad region count']}</td>
            <td>${s.formatPercent(1 - float(patchPerformance['percent correct']))}</td>
        </tr>
        % endfor
    </table>

    % for resultIndex, result in itertools.izip(itertools.count(1), results):
        % if resultIndex in plotPathByIndexByName and 'patchPerformanceByRegion' in plotPathByIndexByName[resultIndex]:
            <h2>Result: ${result['name']}</h2>
            <img src="${plotPathByIndexByName[resultIndex]['patchPerformanceByRegion']}" border=0>
        % endif
    % endfor
</div>


<h1>Locations</h1>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Maximum diameter threshold</td>
            <td>Minimum diameter threshold</td>
            <td>Iterations per burst</td>
            <td>Evaluation radius</td>
            <td>Actual</td>
            <td>Actual not predicted</td>
            <td>Predicted</td>
            <td>Predicted not actual</td>
            <td>AnP/A</td>
            <td>PnA/P</td>
        </tr>
        % for result in results:
        % if 'locations' in result:
        <%
            locationInformation = result['locations']
            if 'performance' not in locationInformation:
                continue
            locationPerformance = locationInformation['performance']
            locationParameters = locationInformation['parameters']
            actual = int(locationPerformance['actual count'])
            actualNotPredicted = int(locationPerformance['actual not predicted count'])
            predicted = int(locationPerformance['predicted count'])
            predictedNotActual = int(locationPerformance['predicted not actual count'])
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${locationParameters['maximum diameter in meters']} meters</td>
            <td>${locationParameters['minimum diameter in meters']} meters</td>
            <td>${locationParameters['iteration count per burst']}</td>
            <td>${locationParameters['evaluation radius in meters']} meters</td>
            <td>${actual}</td>
            <td>${actualNotPredicted}</td>
            <td>${predicted}</td>
            <td>${predictedNotActual}</td>
            <td>
                % if actual:
                    ${s.formatPercent(actualNotPredicted/float(actual))}
                % endif
            </td>
            <td>
                % if predicted:
                    ${s.formatPercent(predictedNotActual/float(predicted))}
                % endif
            </td>
        </tr>
        % endif
        % endfor
    </table>


<h1>Scans</h1>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Window count</td>
            <td>Actual true</td>
            <td>Actual true predicted false</td>
            <td>Predicted true</td>
            <td>Predicted true actual false</td>
            <td>False positive error</td>
            <td>False negative error</td>
            <td>Percent error</td>
            <td>Elapsed time in minutes</td>
        </tr>
        % for result in results:
        <%
            scanProbabilities = result['scans']['probabilities']
            scanProbabilitiesPerformance = scanProbabilities['performance']
            scanProbabilitiesParameters = scanProbabilities['parameters']
            scanProbabilitiesClassifier = scanProbabilities['classifier']
            scanProbabilitiesProbability = scanProbabilities['probability']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${scanProbabilitiesPerformance['window count']}</td>
            <td>${scanProbabilitiesPerformance['actual true']}</td>
            <td>${scanProbabilitiesPerformance['actual true predicted false']}</td>
            <td>${scanProbabilitiesPerformance['predicted true']}</td>
            <td>${scanProbabilitiesPerformance['actual false predicted true']}</td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['false positive error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['false negative error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(scanProbabilitiesPerformance['percent error'], fromDecimal=False)}</td>
            <td>
                % if 'elapsed time in seconds' in scanProbabilitiesPerformance:
                    ${'%0.1f' % (float(scanProbabilitiesPerformance['elapsed time in seconds']) / 60)}
                % endif
            </td>
        </tr>
        % endfor
    </table>
    <br>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Window length</td>
            <td>Window interval</td>
            <td>Image name</td>
            <td class=long>Image coverage</td>
            <td class=long>Region name</td>
            <td>Region coverage</td>
            <td class=long_extra>Classifier name</td>
        </tr>
        % for result in results:
        <%
            scanInformation = result['scans']
            scanProbabilities = scanInformation['probabilities']
            scanProbabilitiesPerformance = scanProbabilities['performance']
            scanProbabilitiesParameters = scanProbabilities['parameters']
            scanProbabilitiesClassifier = scanProbabilities['classifier']
            scanProbabilitiesProbability = scanProbabilities['probability']
            scanWindowLength = float(scanProbabilitiesParameters['window length in meters'])
            scanWindowInterval = scanWindowLength / float(scanProbabilitiesParameters['scan ratio'])
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${scanWindowLength}</td>
            <td>${scanWindowInterval}</td>
            <td class=long>${scanProbabilitiesProbability['image name']}</td>
            <td>\
                % if 'coverage fraction' in scanProbabilitiesParameters:
                    ${s.formatPercent(scanProbabilitiesParameters['coverage fraction'])}\
                % endif
            </td>
            % if 'region name' in scanProbabilitiesProbability:
            <%
                scanRegions = scanInformation['regions']
                scanRegionsParameters = scanRegions['parameters']
            %>
                <td class=long>${scanProbabilitiesProbability['region name']}</td>
                <td>${s.formatPercent(scanRegionsParameters['coverage fraction'])} + ${scanRegionsParameters['coverage offset']}</td>
            % else:
                <td class=long></td>
                <td></td>
            % endif
            <td class=long_extra>${scanProbabilitiesClassifier['name']}</td>
        </tr>
        % endfor
    </table>

<h1>Classifiers</h1>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Test set size</td>
            <td>Actual true</td>
            <td>Actual true predicted false</td>
            <td>Predicted true</td>
            <td>Predicted true actual false</td>
            <td>Test error</td>
            <td>False positive test error</td>
            <td>False negative test error</td>
            <td>Elapsed time in minutes</td>
        </tr>
        % for result in results:
        <%
            classifierInformation = result['classifiers']
            classifierWindows = classifierInformation['windows']
            classifierPerformance = classifierInformation['performance']
            classifierParameters = classifierInformation['parameters']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${classifierPerformance['test set size']}</td>
            <td>${classifierPerformance['actual true']}</td>
            <td>${classifierPerformance['actual true predicted false']}</td>
            <td>${classifierPerformance['predicted true']}</td>
            <td>${classifierPerformance['actual false predicted true']}</td>
            <td>${s.formatPercent(classifierPerformance['test error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(classifierPerformance['false positive test error'], fromDecimal=False)}</td>
            <td>${s.formatPercent(classifierPerformance['false negative test error'], fromDecimal=False)}</td>
            <td>
                % if 'elapsed time in seconds' in classifierPerformance:
                    ${'%0.1f' % (float(classifierPerformance['elapsed time in seconds']) / 60)}
                % endif
            </td>
        </tr>
        % endfor
    </table>
    <br>
    % for resultIndex, result in itertools.izip(itertools.count(1), results):
        <h2>Result: ${result['name']}</h2>
        <img src="${plotPathByIndexByName[resultIndex]['classifierIterationHistory']}" border=0>
    % endfor
    <br>
    <table>
        <tr>
            <td>Result index</td>
            <td>Feature module name</td>
            <td>Feature class name</td>
            <td>Connection table0</td>
            <td>Connection table1</td>
        </tr>
        % for result in results:
        <%
            classifierInformation = result['classifiers']
            classifierParameters = classifierInformation['parameters']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${classifierParameters['feature module name']}</td>
            <td>${classifierParameters['feature class name']}</td>
            <td>${classifierParameters['connection table0 path']}</td>
            <td>${classifierParameters['connection table1 path']}</td>
        </tr>
        % endfor
    </table>
    <br>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Classifier module name</td>
            <td>Length0</td>
            <td>Ratio0</td>
            <td>Length1</td>
            <td>Ratio1</td>
            <td>Hidden count</td>
            <td>Dataset name</td>
        </tr>
        % for result in results:
        <%
            classifierInformation = result['classifiers']
            classifierParameters = classifierInformation['parameters']
            classifierDataset = classifierInformation['dataset']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${classifierParameters['classifier module name']}</td>
            <td>${classifierParameters['length0']}</td>
            <td>${classifierParameters['ratio0']}</td>
            <td>${classifierParameters['length1']}</td>
            <td>${classifierParameters['ratio1']}</td>
            <td>${classifierParameters['hidden count']}</td>
            <td>${classifierDataset['name']}</td>
        </tr>
        % endfor
    </table>


<h1>Datasets</h1>
<table>
    <tr>
        <td class=long>Result name</td>
        <td>Positive fraction</td>
        <td>Maximum training size</td>
        <td>Maximum test size</td>
        <td>Training positive</td>
        <td>Training negative</td>
        <td>Training total</td>
        <td>Test positive</td>
        <td>Test negative</td>
        <td>Test total</td>
    </tr>
    % for result in results:
    <%
        datasetInformation = result['datasets']
        datasetTrainingSet = datasetInformation['training set']
        datasetTestSet = datasetInformation['test set']
        datasetParameters = datasetInformation['parameters']
    %>
    <tr>
        <td class=long>${result['name']}</td>
        <td>${datasetParameters['positive fraction']}</td>
        <td>${datasetParameters['training size']}</td>
        <td>${datasetParameters['test size']}</td>
        <td>${datasetTrainingSet['positive']}</td>
        <td>${datasetTrainingSet['negative']}</td>
        <td>${datasetTrainingSet['total']}</td>
        <td>${datasetTestSet['positive']}</td>
        <td>${datasetTestSet['negative']}</td>
        <td>${datasetTestSet['total']}</td>
    </tr>
    % endfor
</table>
<br>
<table>
    <tr>
        <td class=long>Result name</td>
        <td>Window length</td>
        <td class=long_extra>Window names</td>
        <td class=long_extra>Patch names</td>
    </tr>
    % for result in results:
    <%
        datasetInformation = result['datasets']
        datasetWindows = datasetInformation['windows']
        datasetSources = datasetInformation['sources']
    %>
    <tr>
        <td class=long>${result['name']}</td>
        <td>${datasetWindows['window length in meters']} meters</td>
        <td class=long_extra>${s.unstringifyListAsLine(datasetSources['window names'])}</td>
        <td class=long_extra>${s.unstringifyListAsLine(datasetSources['patch names'])}</td>
    </tr>
    % endfor
</table>


<h1>Sources</h1>
    <h2>Windows</h2>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Source window index</td>
            <td>Shift count</td>
            <td>Multispectral pixel shift value</td>
            <td>Example count per region</td>
            <td>Window length</td>
        </tr>
        % for result in results:
        <%
            sources = result['sources']['windows']
        %>
        % for sourceIndex, source in itertools.izip(itertools.count(1), sources):
        <%
            sourceWindows = source['windows']
            sourceWindowParameters = sourceWindows['parameters']
            sourceWindowWindows = sourceWindows['windows']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${sourceIndex}</td>
            <td>${sourceWindowParameters.get('shift count', 0)}</td>
            <td>${sourceWindowParameters.get('multispectral pixel shift value', 0)}</td>
            <td>${sourceWindowParameters['example count per region']}</td>
            <td>${sourceWindowWindows['window length in meters']} meters</td>
        </tr>
        % endfor
        % endfor
    </table>
    <br>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Source window index</td>
            <td>Training positive</td>
            <td>Training positive shifted</td>
            <td>Training negative</td>
            <td>Training total</td>
            <td>Test positive</td>
            <td>Test positive shifted</td>
            <td>Test negative</td>
            <td>Test total</td>
        </tr>
        % for result in results:
        <%
            sources = result['sources']['windows']
        %>
        % for sourceIndex, source in itertools.izip(itertools.count(1), sources):
        <%
            sourceWindows = source['windows']
            sourceWindowTrainingSet = sourceWindows['training set']
            sourceWindowTestSet = sourceWindows['test set']
            sourceWindowExamples = sourceWindows['examples']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${sourceIndex}</td>
            <td>${sourceWindowExamples['training_positive count']}</td>
            <td>${sourceWindowExamples['training_positive_shifted count']}</td>
            <td>${sourceWindowExamples['training_negative count']}</td>
            <td>${sourceWindowTrainingSet['total']}</td>
            <td>${sourceWindowExamples['test_positive count']}</td>
            <td>${sourceWindowExamples['test_positive_shifted count']}</td>
            <td>${sourceWindowExamples['test_negative count']}</td>
            <td>${sourceWindowTestSet['total']}</td>
        </tr>
        % endfor
        % endfor
    </table>
    <br>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Source window index</td>
            <td class=long>Region name</td>
            <td>Region coverage</td>
            <td>Region count</td>
            <td>Region test fraction</td>
            <td class=long>Region length</td>
        </tr>
        % for result in results:
        <%
            sources = result['sources']['windows']
        %>
        % for sourceIndex, source in itertools.izip(itertools.count(1), sources):
        <%
            sourceWindowRegions = source['windows']['regions']
            sourceRegions = source['regions']
            sourceRegionRegions = sourceRegions['regions']
            sourceRegionParameters = sourceRegions['parameters']
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${sourceIndex}</td>
            <td class=long>${sourceWindowRegions['name']}</td>
            <td>
            % if 'coverage fraction' in sourceRegionParameters:
                ${s.formatPercent(sourceRegionParameters['coverage fraction'])} 
                + 
                ${sourceRegionParameters['coverage offset']}
            % endif
            </td>
            <td>${sourceWindowRegions['count']}</td>
            <td>${sourceRegionParameters['test fraction per region']}</td>
            <td class=long>
            % if 'region length in windows' in sourceRegionParameters:
                ${sourceRegionParameters['region length in windows']} windows (${float(sourceRegionParameters['region length in windows']) * float(sourceRegionParameters['window length in meters'])} meters)
            % endif
            </td>
        </tr>
        % endfor
        % endfor
    </table>


    <h2>Patches</h2>
    <table>
        <tr>
            <td class=long>Result name</td>
            <td>Source patch index</td>
            <td>Region count</td>
            <td>Performance mean</td>
            <td>Performance standard deviation</td>
            <td>Performance threshold</td>
            <td>Bad region count</td>
            <td>Percent error over regions</td>
        </tr>
        % for result in results:
        <%
            sources = result['sources']['patches']
        %>
        % for sourceIndex, source in itertools.izip(itertools.count(1), sources):
        <%
            patchInformation = source['patches']
            if patchInformation and 'performance by region' in patchInformation:
                patchPerformance = patchInformation['performance']
                patchPerformanceByRegion = patchInformation['performance by region']
                patchParameters = patchInformation['patches']
                patchRegionPerformances = [float(x) for x in patchPerformanceByRegion.values()]
            else:
                continue
        %>
        <tr>
            <td class=long>${result['name']}</td>
            <td>${sourceIndex}</td>
            <td>${patchPerformance['region count']}</td>
            <td>${s.formatPercent(numpy.mean(patchRegionPerformances))}</td>
            <td>${s.formatPercent(numpy.std(patchRegionPerformances))}</td>
            <td>${s.formatPercent(patchParameters['minimum percent correct'])}</td>
            <td>${patchPerformance['bad region count']}</td>
            <td>${s.formatPercent(1 - float(patchPerformance['percent correct']))}</td>
        </tr>
        % endfor
        % endfor
    </table>

    % for resultIndex, result in itertools.izip(itertools.count(1), results):
        % for sourceIndex, source in itertools.izip(itertools.count(1), sources):
        <%
            sources = result['sources']
            plotName = '%s_patchPerformanceByRegion' % sourceIndex
        %>
        % if resultIndex in plotPathByIndexByName and plotName in plotPathByIndexByName[resultIndex]:
        <h2>Result: ${result['name']} (Patch source ${sourceIndex})</h2>
            <img src="${plotPathByIndexByName[resultIndex][plotName]}" border=0>
        % endif
    % endfor
    % endfor
</div>


</body>
</html>
