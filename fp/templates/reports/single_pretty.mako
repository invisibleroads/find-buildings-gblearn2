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
    width: 8em;
    text-align: right;
}
.indented {margin-left: 2em}
</style>
</head>


<body>
<%namespace name="s" file="shared.mako"/>
<% 
    import itertools 
%>


Result: ${result['name']}


<%def name="tabulateDatasetSizes(trainingInformation, testInformation)">
<table>
    <tr>
        <td></td>
        <td>Positive</td>
        <td>Negative</td>
        <td>Total</td>
    </tr>
    <tr>
        <td>Training set</td>
        <td>${trainingInformation['positive']}</td>
        <td>${trainingInformation['negative']}</td>
        <td>${trainingInformation['total']}</td>
    </tr>
    <tr>
        <td>Test set</td>
        <td>${testInformation['positive']}</td>
        <td>${testInformation['negative']}</td>
        <td>${testInformation['total']}</td>
    </tr>
</table>
</%def>


<%def name="showImageInformation(information)">
    <%
        multispectralImage = information['multispectral image']
        panchromaticImage = information['panchromatic image']
        positiveLocation = information['positive location']
    %>
    <p>
    Multispectral image path = ${multispectralImage['path']}<br>
    Multispectral image dimensions = ${multispectralImage['width in pixels']}x${multispectralImage['height in pixels']} pixels<br>
    <br>
    Panchromatic image path = ${panchromaticImage['path']}<br>
    Panchromatic image dimensions = ${panchromaticImage['width in pixels']}x${panchromaticImage['height in pixels']} pixels<br>
    <br>
    Positive location path = ${positiveLocation['path']}<br>
    Positive location count = ${positiveLocation['count']}<br>
    <br>
    Spatial reference = ${multispectralImage['spatial reference']}<br>
    </p>
</%def>


<%def name="showPatchInformation(information, level, targetInner)">
% if 'performance by region' in information:
<%
    patchPerformance = information['performance']
    patchPerformanceByRegion = information['performance by region']
    patchTrainingSet = information['training set']
    patchTestSet = information['test set']
    patchParameters = information['patches']
    patchWindows = information['windows']
%>
    <h${level}>Patch Performance</h${level}>
    <p>A region is bad if less than ${s.formatPercent(patchParameters['minimum percent correct'])} of its windows are correct.</p>
    <table>
        <tr>
            <td>Region count</td>
            <td>Bad region count</td>
            <td>Percent error over regions</td>
        </tr>
        <tr>
            <td>${patchPerformance['region count']}</td>
            <td>${patchPerformance['bad region count']}</td>
            <td>${s.formatPercent(1 - float(patchPerformance['percent correct']))}</td>
        </tr>
    </table>


    <h${level}>Patch Performance by region</h${level}>
    <img src="${plotPathByName[targetInner]}" border=0>
    <table>
        <tr>
            <td>Left</td>
            <td>Top</td>
            <td>Right</td>
            <td>Bottom</td>
            <td>Percent correct over windows inside region</td>
        </tr>
        % for regionFrame, windowPercentCorrect in patchPerformanceByRegion.iteritems():
            <%
            left, top, right, bottom = regionFrame.split()
            %>
        <tr>
            <td class="number ">${left}</td>
            <td class="number ">${top}</td>
            <td class="number ">${right}</td>
            <td class="number ">${bottom}</td>
            <td class="number ">${s.formatPercent(windowPercentCorrect)}</td>
        </tr>
        % endfor
    </table>
    <p>
    Probability name = ${patchParameters['probability name']}<br>
    Probability path = ${patchParameters['probability path']}<br>
    </p>


    <h${level}>Patch windows sampled from bad regions</h${level}>
    <p>We sampled ${patchParameters['patch count per region']} windows from each bad region.</p>
    ${tabulateDatasetSizes(patchTrainingSet, patchTestSet)}
    <p>
    Spatial reference = ${patchWindows['spatial reference']}<br>
    Window length in meters = ${patchWindows['window length in meters']}<br>
    </p>
% endif
</%def>


<%def name="showScanInformation(information, level)">
<%
    scanProbabilities = information['probabilities']
    scanProbabilitiesPerformance = scanProbabilities['performance']
    scanProbabilitiesParameters = scanProbabilities['parameters']
    scanProbabilitiesClassifier = scanProbabilities['classifier']
    scanProbabilitiesProbability = scanProbabilities['probability']
%>
    <h${level}>Scan performance</h${level}>
    <table>
        <tr>
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
        <tr>
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
    </table>
    <%
    scanWindowLengthInMeters = float(scanProbabilitiesParameters['window length in meters'])
    %>
    <p>
    The scanning window was ${scanWindowLengthInMeters} meters high and ${scanWindowLengthInMeters} meters wide and incremented every ${scanWindowLengthInMeters / float(scanProbabilitiesParameters['scan ratio'])} meters horizontally and vertically.<br>
    </p>
    <p>
    We used the following classifier to generate the window probabilities:<br>
    Classifier name = ${scanProbabilitiesClassifier['name']}<br>
    Classifier path = ${scanProbabilitiesClassifier['path']}<br>
    </p>
    <p>
    We scanned the following regions of the following image:<br>
    % if 'region name' in scanProbabilitiesProbability:
        Region name = ${scanProbabilitiesProbability['region name']}<br>
    % endif
    Region path = ${scanProbabilitiesProbability['region path']}<br>
    Image name = ${scanProbabilitiesProbability['image name']}<br>
    Image path = ${scanProbabilitiesProbability['image path']}<br>
    </p>
    <h${level}>Scan parameters</h${level}>
    % if 'regions' in information:
        <%
        scanRegions = information['regions']
        scanRegionsRegions = scanRegions['regions']
        scanRegionsTestRegions = scanRegions['test regions']
        scanRegionsParameters = scanRegions['parameters']
        regionLengthInWindows = float(scanRegionsParameters['region length in windows'])
        regionLengthInMeters = regionLengthInWindows * float(scanRegionsParameters['window length in meters'])
        %>
        <p>
        There were ${scanRegionsRegions['count']} scanned regions.<br>
        % if 'coverage fraction' in scanRegionsParameters:
             The regions covered ${s.formatPercent(scanRegionsParameters['coverage fraction'])} of the image with an offset of ${scanRegionsParameters['coverage offset']}.<br>
        % endif
        Each region was ${regionLengthInWindows} windows (${regionLengthInMeters} meters) wide and ${regionLengthInWindows} windows (${regionLengthInMeters} meters) high and contained ${regionLengthInWindows ** 2} non-overlapping windows.
        </p>
    % elif 'coverage fraction' in scanProbabilitiesParameters:
        <p>
        We scanned ${s.formatPercent(scanProbabilitiesParameters['coverage fraction'])} of the image.<br>
        </p>
    % endif
    <h${level}>Scanned image</h${level}>
    ${showImageInformation(information['images'])}
</%def>


% if result['patches']:
<h1>Patches</h1>
<div class=indented>
    ${showPatchInformation(result['patches'], 2, 'patchPerformanceByRegion')}
</div>
% endif


% if 'locations' in result:
<h1>Locations</h1>
<%
    locationInformation = result['locations']
    locationProbability = locationInformation['probability']
    locationLocation = locationInformation['location']
    locationParameters = locationInformation['parameters']
%>
<div class=indented>
    % if 'performance' in locationInformation:
        <%
            locationPerformance = locationInformation['performance']
        %>
        <h2>Location performance</h2>
        <p>
        A predicted location is considered not actual if there is no actual location within ${locationParameters['evaluation radius in meters']} meters of the predicted location.<br>
        An actual location is considered not predicted if there is no predicted location within ${locationParameters['evaluation radius in meters']} meters of the actual location.<br>
        </p>
        <table>
            <tr>
                <td>Actual</td>
                <td>Actual not predicted</td>
                <td>Predicted</td>
                <td>Predicted not actual</td>
            </tr>
            <tr>
                <td>${locationPerformance['actual count']}</td>
                <td>${locationPerformance['actual not predicted count']}</td>
                <td>${locationPerformance['predicted count']}</td>
                <td>${locationPerformance['predicted not actual count']}</td>
            </tr>
        </table>
        <p>
        % if 'actual location path' in locationPerformance:
        Actual location path = ${locationPerformance['actual location path']}<br>
        % endif
        Predicted location path = ${locationLocation['path']}<br>
        Spatial reference = ${locationLocation['spatial reference']}<br>
        </p>
    % endif
    <h2>Location parameters</h2>
    <p>
    We removed locations whose probability cluster was smaller than ${locationParameters['minimum diameter in meters']} meters.<br>
    We burst probability clusters larger than ${locationParameters['maximum diameter in meters']} meters.<br>
    For each burst, we ran the k-means algorithm for ${locationParameters['iteration count per burst']} iterations.<br>
    </p>
    <p>
    We clustered the following window probabilities to generate the locations:<br>
    Probability name = ${locationProbability['name']}<br>
    Probability path = ${locationProbability['path']}<br>
    </p>
</div>
% endif


<h1>Scans</h1>
<div class=indented>
    ${showScanInformation(result['scans'], 2)}
</div>


<h1>Classifiers</h1>
<%
    classifierInformation = result['classifiers']
    classifierWindows = classifierInformation['windows']
    classifierPerformance = classifierInformation['performance']
    classifierParameters = classifierInformation['parameters']
    classifierDataset = classifierInformation['dataset']

    classifierIterationHistory = eval(classifierPerformance['iteration history'])
    classifierIterationHistory.reverse()
    classifierIterationIndex = int(classifierPerformance['iteration index'])
    classifierTestPercentError, classifierTrainingPercentError = classifierIterationHistory[classifierIterationIndex - 1][:2]
%>
<div class=indented>
    <h2>Performance</h2>
    <table>
        <tr>
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
        <tr>
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
    </table>
    <h2>Training</h2>
    <img src="${plotPathByName['classifierIterationHistory']}" border=0>
    <p>
    We took the classifier from iteration ${classifierIterationIndex} with a ${s.formatPercent(classifierTrainingPercentError, fromDecimal=False)} training error and a ${s.formatPercent(classifierTestPercentError, fromDecimal=False)} test error.
    </p>
    <h2>Parameters</h2>
    <p>
    The first convolution kernel was ${classifierParameters['length0']}x${classifierParameters['length0']} pixels.<br>
    The first subsampling ratio was ${classifierParameters['ratio0']}<br>
    The second convolution kernel was ${classifierParameters['length1']}x${classifierParameters['length1']} pixels.<br>
    The second subsampling ratio was ${classifierParameters['ratio1']}<br>
    There were ${classifierParameters['hidden count']} hidden units in the hidden layer.<br>
    </p>
    <p>
    Classifier module name = ${classifierParameters['classifier module name']}<br>
    Feature module name = ${classifierParameters['feature module name']}<br>
    Feature class name = ${classifierParameters['feature class name']}<br>
    Connection table path from input layer to first layer = ${classifierParameters['connection table0 path']}<br>
    Connection table path from first layer to second layer = ${classifierParameters['connection table1 path']}<br>
    </p>
    <p>
    Dataset path = ${classifierDataset['path']}<br>
    Dataset name = ${classifierDataset['name']}<br>
    Training path = ${classifierWindows['training']}<br>
    Test path = ${classifierWindows['test']}<br>
    </p>
</div>


<h1>Datasets</h1>
<%
    datasetInformation = result['datasets']
    datasetWindows = datasetInformation['windows']
    datasetSources = datasetInformation['sources']
    datasetTrainingSet = datasetInformation['training set']
    datasetTestSet = datasetInformation['test set']
    datasetParameters = datasetInformation['parameters']
%>
<div class=indented>
    <h2>Statistics</h2>
    ${tabulateDatasetSizes(datasetTrainingSet, datasetTestSet)}
    <p>
    Window length in meters = ${datasetWindows['window length in meters']}<br>
    Spatial reference = ${datasetWindows['spatial reference']}<br>
    </p>
    <h2>Parameters</h2>
    Positive fraction = ${datasetParameters['positive fraction']}<br>
    Training size = ${datasetParameters['training size']}<br>
    Test size = ${datasetParameters['test size']}<br>
    ${s.unstringifyList('Window names', datasetSources['window names'])}
    ${s.unstringifyList('Patch names', datasetSources['patch names'])}
</div>


<h1>Sources</h1>
<%
    from libraries import store
    windowNames = store.unstringifyStringList(datasetSources['window names'])
    patchNames = store.unstringifyStringList(datasetSources['patch names'])
    sourceInformation = result['sources']
    sourceWindowInformation = sourceInformation['windows']
    sourcePatchInformation = sourceInformation['patches']
%>
<div class=indented>
    % for sourceIndex, information, windowName in itertools.izip(itertools.count(1), sourceWindowInformation, windowNames):
        <h2>Source window ${sourceIndex}: ${windowName}</h2>
        <div class=indented>
            <%
            sourceWindows = information['windows']
            sourceWindowWindows = sourceWindows['windows']
            sourceWindowRegions = sourceWindows['regions']
            sourceWindowTrainingSet = sourceWindows['training set']
            sourceWindowTestSet = sourceWindows['test set']
            sourceWindowExamples = sourceWindows['examples']
            sourceWindowParameters = sourceWindows['parameters']
            shiftCount = int(sourceWindowParameters.get('shift count', 0))
            sourceRegions = information['regions']
            sourceRegionRegions = sourceRegions['regions']
            sourceRegionParameters = sourceRegions['parameters']
            sourceImages = information['images']
            %>
            <p>
            We sampled ${sourceWindowParameters['example count per region']} examples from each region.<br>
            % if shiftCount:
                To increase the number of positive examples, we shift-copied each positive example 
                % if shiftCount == 1:
                    once.<br>
                % else:
                    ${shiftCount} times.<br>
                % endif
                Each shift was a random ${sourceWindowParameters.get('multispectral pixel shift value', 0)}-pixel displacement from its original location in the multispectral image.<br>
            % endif
            </p>
            <p>
            Window length in meters = ${sourceWindowWindows['window length in meters']}<br>
            Spatial reference = ${sourceWindowWindows['spatial reference']}<br>
            </p>
            <table>
                <tr>
                    <td></td>
                    <td>Positive</td>
                    <td>Positive shifted</td>
                    <td>Negative</td>
                    <td>Total</td>
                </tr>
                <tr>
                    <td>Training</td>
                    <td>${sourceWindowExamples['training_positive count']}</td>
                    <td>${sourceWindowExamples['training_positive_shifted count']}</td>
                    <td>${sourceWindowExamples['training_negative count']}</td>
                    <td>${sourceWindowTrainingSet['total']}</td>
                </tr>
                <tr>
                    <td>Test</td>
                    <td>${sourceWindowExamples['test_positive count']}</td>
                    <td>${sourceWindowExamples['test_positive_shifted count']}</td>
                    <td>${sourceWindowExamples['test_negative count']}</td>
                    <td>${sourceWindowTestSet['total']}</td>
                </tr>
            </table>
            <p>
            Region name = ${sourceWindowRegions['name']}<br>
            Region path = ${sourceWindowRegions['path']}<br>
            Region count = ${sourceWindowRegions['count']}<br>
            </p>
            <p>
            Test fraction per region = ${sourceRegionParameters['test fraction per region']}<br>
            % if 'coverage fraction' in sourceRegionParameters:
                Coverage fraction = ${sourceRegionParameters['coverage fraction']}<br>
                Coverage offset = ${sourceRegionParameters['coverage offset']}<br>
            % endif
            Window length in meters = ${sourceRegionParameters['window length in meters']}<br>
            % if 'region length in windows' in sourceRegionParameters:
                Region length in windows = ${sourceRegionParameters['region length in windows']}<br>
            % endif
            </p>
            <p>
            Image name = ${sourceRegionParameters['image name']}<br>
            Image path = ${sourceRegionParameters['image path']}<br>
            </p>
            <p>
            ${showImageInformation(sourceImages)}
            </p>
        </div>
    % endfor

    % for sourceIndex, information, patchName in itertools.izip(itertools.count(1), sourcePatchInformation, patchNames):
        <h2>Source patch ${sourceIndex}: ${patchName}</h2>
        <div class=indented>
            <%
            sourcePatches = information['patches']
            %>
            ${showPatchInformation(sourcePatches, 3, '%s_patchPerformanceByRegion' % sourceIndex)}
            ${showScanInformation(information, 3)}
        </div>
    % endfor
</div>


</body>


</html>
