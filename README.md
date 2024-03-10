# Access Kaiser Health Data via iPhone and Apple Health

This repository shows how I am exploring my downloaded Kaiser medical record data. 

## Disclaimer
I am not medically trained, and have no documentation on the file format. This code is NOT for making medical decisions. There may be missing data and actual errors. I recommend discussing anything interesting you find with your doctor.

## Why?
My initial goal is to graph my weight and blood-pressure over time. Kaiser's app allows you to graph test results, but I have not found a way to graph vital sign recording over time. You can look at each record, one at a time, but who wants to do that?

# How to get your data

1. What I did was go to the Apple Health app on my iPhone. 
2. Selected my profile picture to open my profile. 
2. Select "Health Records". "Add Accounts", and follow the prompts to add Kaiser.
3. The go back to the profile and select "Export All Data". This exports ALL your Apple Health data. So you not only get Kaiser medical records, but all records from Apple Health, including frequent updates from  your apple watch! The process took a couple of minutes. My health data was about 50MB, with an earliest record in 2007.  I assume that's when Kaiser went digital, since it's long before any other Apple Health data.
4. For me, it offered an airdrop option to my mac, but you can save it to files, I think, and move it where you want from there.
5. What you get is a single zip file. When you expand it, you get a large (1GB in my case) file, with various types. I see json, gpx, xml and more. 
6. Explore!

All of the above should be possible without an iPhone, but that's how I did it.

I'm using Kaiser Northern California. I believe this will work with other Kaiser groups, but I have not tested it.

# Running the Code
All that is currently implemented is fetchig "Conditions" and printing weight records. 

It assumes your zip is expanded to the 'export' directory, in the current directory.

```python health.py```


