# Covid-19 Europe Dashboard (by Dominik Macko)

The main motivation was to create a simple dashboard for Covid-19 data in Europe that could not be misinterpreted by looking at absolute numbers. Thus, the goal was to use only relative per capita metrics for deaths, tests, cases, ...

## Data

The original idea was to use data from John Hopkins University and add additional data from other sources. However, after some time I discovered that [OurWorldInData](https://github.com/owid/covid-19-data/tree/master/public/data/) has already done so. Thus, I used their data. From the data I selected eights columns to visualize (all in relative values, not absolute):

- new cases
- new tests
- new deaths
- new vaccinations
- hospitalized patients
- hospitalized patients in ICU
- weekly ICU admissions
- weekly hospitalization admissions

Then to preprocess data I filled missing values by zeroes for new vaccinations, new deaths, new cases, and new tests. The rationale behind this was that missing values should most likely mean the country did not report anything for given day because they either didn't have anything to report or reported it on some other day in a batch. Then I also saw in the data that ICU patients and hospitalized patients had often missing values. Thus, for each country I filled the missing values by the data that was recorded in the closest proximity. I also converted negative values to zero for each colum. 

## Technologies

For the project, I used Python 3, Plotly, and Dash. These technologies were selected because I was previously already familiar with Python and Plotly. Thus, Dash was naturally chosen because it is easy to use on top of Plotly.  

## Visualization details

![image-20220130191046383](/home/dominik/.var/app/io.typora.Typora/config/Typora/typora-user-images/image-20220130191046383.png)

For the visualization I used a simple layout of two graphs which provide different views on the data, two dropdowns, date slider, and selection interaction on the map.
The first dropdown allows the user to select whether he wants to display mean or total (sum) values on the map for the given date range.
The second dropdown allows the user select which column (metric) he wishes to visualize.
The date slider allows the user to select the date range for which he wants to visualize the data. The slider displays the lowest, the highest, and the currently selected dates. Dash does not support date slider, so this is a range slider hacked to work with dates.
The first graph is a choropleth map of Europe and displays the selected data. For columns where higher value is better (new vaccinations, new tests) green colors are used. For the other columns green color is used. This graph also supports clicking on countries or selecting them which leads to only these countries being displayed in the second graph.
The second graph (the right one) displays time evolution of the selected column for the given date range. It also takes into account the countries selected in the first graph.

## Further improvements

There are many things that could be further improved.
The first issue is connected to the choropleth map. I was not able to change the legend of the selected column ("mean covid-19 hospitalized patients" in the picture above) to be shown vertically. And because of this the size of the map is not as big as would be ideal. But also the map size sometimes changes because of different string lengths of the legends.
The second minor issue concerns the country selection mechanisms on the map. I wanted to add an option that clicking on the ocean/sea would signal selecting all countries. But I was unable to find a way to do so. Because of this, when the user wants to go from a selected subset of countries to all the countries being selected, he has only one option -- select all the countries manually.
It might be also better to further improve data preprocessing and instead of filling zeroes do something smarter.
Another possible improvement would be to include additional data when clicking a single country -- for example display the specific data but further stratified by age (https://ockovani.opendatalab.cz/statistiky_srovnani). However, this would include scrapping different data for each country and would complicate the project (and I didn't have as much time). Also when selecting many countries there could be possibly another graph (circle graph maybe) that would compare their sizes.