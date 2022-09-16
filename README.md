# fixedissues for Splunk Enterprise and TAs

Do you think splunk release notes are valuable? Well, I think so. Unfortunately, there is no good overview of which release fixes which issue. 
Of course you could go to the website and check out the [release notes](https://docs.splunk.com/Documentation/Splunk/latest/ReleaseNotes/Knownissues) for your product version, but what if you really want to "work" with it?

## Purpose of this app

This app lists "fixed issues" for Splunk version 7.0 till the recent release. It should help you to find out if a certain issue might be fixed..

e.g.: if you are facing a specific issue with charting and you are running Splunk v8.1.2 you would have to check 9 newer releases to find out what issues had been fixed to todays v8.2.3.

This Apps helps you to do this job with a single click. Select you version and/or category and it will display all 6 issues which were solved in further versions.

## Installation

Just put the app on any searchhead or single-instance. There is no need to run it in production, it's more to help the splunk admin and/or devs.

## Where does the data come from?

Data is generated from Splunk [docs.splunk.com](docs.splunk.com) Webpage and stored in csv files as lookup.

## Products

- Splunk Enterprise v7.0.0-latest
- Splunk db connect v3.*
