import urllib2
from lxml.html.soupparser import fromstring
import plotly
import plotly.graph_objs as go

SCORES_URL = "http://www.gridsagegames.com/cogmind/scores"
NUMBER_OF_LEVELS = 12

COLOR_SOURCE = """.score-SCR, .score-SCR a, .score-SCR a:visited:hover { color: #665233; }
.score-MAT, .score-MAT a, .score-MAT a:visited:hover { color: #9e8664; }
.score-FAC, .score-FAC a, .score-FAC a:visited:hover { color: #9e9e9e; }
.score-RES, .score-RES a, .score-RES a:visited:hover { color: #bf00ff; }
.score-ACC, .score-ACC a, .score-ACC a:visited:hover { color: #dedede; }
.score-SUR, .score-SUR a, .score-SUR a:visited:hover { color: #00e100; }
.score-MIN, .score-MIN a, .score-MIN a:visited:hover { color: #666666; }
.score-STO, .score-STO a, .score-STO a:visited:hover { color: #b25900; }
.score-REC, .score-REC a, .score-REC a:visited:hover { color: #b25900; }
.score-WAS, .score-WAS a, .score-WAS a:visited:hover { color: #665233; }
.score-GAR, .score-GAR a, .score-GAR a:visited:hover { color: #b20000; }
.score-LOW, .score-LOW a, .score-LOW a:visited:hover { color: #665233; }
.score-UPP, .score-UPP a, .score-UPP a:visited:hover { color: #665233; }
.score-PRO, .score-PRO a, .score-PRO a:visited:hover { color: #665233; }
.score-DEE, .score-DEE a, .score-DEE a:visited:hover { color: #665233; }
.score-ZIO, .score-ZIO a, .score-ZIO a:visited:hover { color: #665233; }
.score-DAT, .score-DAT a, .score-DAT a:visited:hover { color: #665233; }
.score-ZHI, .score-ZHI a, .score-ZHI a:visited:hover { color: #9e8664; }
.score-WAR, .score-WAR a, .score-WAR a:visited:hover { color: #b22d00; }
.score-EXT, .score-EXT a, .score-EXT a:visited:hover { color: #848400; }
.score-CET, .score-CET a, .score-CET a:visited:hover { color: #848400; }
.score-ARC, .score-ARC a, .score-ARC a:visited:hover { color: #848400; }
.score-HUB, .score-HUB a, .score-HUB a:visited:hover { color: #848400; }
.score-ARM, .score-ARM a, .score-ARM a:visited:hover { color: #ff0000; }
.score-LAB, .score-LAB a, .score-LAB a:visited:hover { color: #dedede; }
.score-QUA, .score-QUA a, .score-QUA a:visited:hover { color: #00b200; }
.score-TES, .score-TES a, .score-TES a:visited:hover { color: #00b200; }
.score-SEC, .score-SEC a, .score-SEC a:visited:hover { color: #00b200; }
.score-COM, .score-COM a, .score-COM a:visited:hover { color: #00a3d9; }
.score-AC0, .score-AC0 a, .score-AC0 a:visited:hover { color: #dedede; }"""

def create_trace(location, yvals):
    """Creates an object that can be added to the graph"""
    if yvals[NUMBER_OF_LEVELS-1] == 0:
        abbrev = location[:3].upper()
    else:
        abbrev = "SUR"
    trace = go.Bar(
        x=list(range(-(NUMBER_OF_LEVELS-1), 1)), #-11 - 0, for example
        y=yvals,
        name=location,
        marker=dict(
            color=colors[abbrev],
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        )
    )
    return trace

def adjusted_location(location):
    """Adjusted the location name so that their abbreviation is more useful"""
    dic = {
        "L. Caves": "Lower Caves",
        "U. Caves": "Upper Caves",
        "P. Caves": "Proximity Caves",
        "D. Caves": "Deep Caves"
    }

    location = location.strip()
    if "/" not in location:
        return location
    else:
        location_name = location.split("/")[1]
        if location_name in dic:
            location = location.split("/")[0] + "/" + dic[location_name]
        return location

def get_web_source(url):
    """returns: the source code from the high scores website"""
    page = urllib2.urlopen(url)
    data = page.read()
    return data

def get_list_of_locations(source_code):
    """:returns: a list of players' best final locations"""
    locations = []
    root = fromstring(source_code)
    tbody = root.xpath('//*[@id="wrapContent"]/div[3]/div[2]/table')
    for tr in tbody[0]:
        locations.append(tr[2][0].text)
    return locations

if __name__ == "__main__":
    colors = {}
    for line in COLOR_SOURCE.splitlines():
        abbrev = line.split("-")[1].split(",")[0]
        hexa = line.split("#")[1].split(";")[0]
        color_parts = hexa[0:2], hexa[2:4], hexa[4:6]
        color_parts = (int(i, 16) for i in color_parts)
        color_string = "rgb({},{},{})".format(*color_parts) #rgb(255,255,255) for example
        colors[abbrev] = color_string

    locations = get_list_of_locations(get_web_source(SCORES_URL))
    
    yvals = {}
    for location in locations:
        location = adjusted_location(location)
        if "/" in location:
            #Use the level that is written with the location
            level = NUMBER_OF_LEVELS - 1 + int(location.split("/")[0])
            location_name = location.split("/")[1]
        else:
            #Ascended scores are treated as though they are the max level
            level = NUMBER_OF_LEVELS - 1
            location_name = location
        if location_name not in yvals:
            yvals[location_name] = [0] * NUMBER_OF_LEVELS
        yvals[location_name][level] += 1

    traces = []
    for location in yvals:
        traces.append(create_trace(location, yvals[location]))

    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=traces, layout=layout)
    
    plotly.plotly.plot(fig, filename='online_cogmind_scores')
    
    #For testing
    #plotly.offline.plot(fig, filename='online_cogmind_scores.html')
