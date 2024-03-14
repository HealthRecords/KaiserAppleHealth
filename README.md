# Access Kaiser Health Data via iPhone and Apple Health

This repository shows how I am exploring my downloaded Kaiser medical record data. 

## Disclaimer
I am not medically trained, and have no documentation on the file format. This code is NOT for making medical decisions. There may be missing data and actual errors. I recommend discussing anything interesting you find with your doctor.

## Why?
My initial goal is to graph my weight and blood-pressure over time. Kaiser's app allows you to graph test results, but I have not found a way to graph vital signs recorded over time. You can look at each record, one at a time, but who wants to do that?

# How to Get Your Kaiser Medical Record data

1. What I did was go to the Apple Health app on my iPhone. 
2. Selected my profile picture to open my profile. 
2. Select "Health Records". "Add Accounts", and follow the prompts to add Kaiser.
3. The go back to the profile and select "Export All Data". This exports ALL your Apple Health data. So you not only get Kaiser medical records, but all records from Apple Health, including frequent updates from  your apple watch! The process took a couple of minutes. My health data was about 50MB, with an earliest record in 2007.  I assume that's when Kaiser went digital, since it's long before any other Apple Health data.
4. For me, it offered an airdrop option to my mac, but you can save it to files, I think, and move it where you want from there.
5. What you get is a single zip file. When you expand it, you get a large (1GB in my case) directory of files. It looks like all of the Kaiser files are json.
6. Explore!

All of the above should be possible without an iPhone, but that's how I did it.

I'm using Kaiser Northern California. I believe this will work with other Kaiser groups, but I have not tested it. 

I believe this data format may be a [standard format](https://www.healthit.gov/faq/what-are-differences-between-electronic-medical-records-electronic-health-records-and-personal), so this code may work with more than just Kaiser.

# Running the Code
It assumes your zip is expanded to the 'export' directory, in the current directory.

I am using python 3.12.2

```python health.py --help```

```python health.py --stat Weight --plot ```

# Notes
There are many more types of entries that are not yet supported. Run python --categories to see the list
It's simple to add support for more types. 

```
python --categories

Laboratory                      :   338
Lab                             :   332
Vital Signs                     :   116
Clinical Note                   :    59
Outpatient                      :    25
Inpatient                       :    12
Community                       :    21
```
