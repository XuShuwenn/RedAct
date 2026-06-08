# Cox Proportional Hazards Model Task

Given survival data in `/root/input.csv`, fit a Cox proportional hazards model and extract the concordance index.

The CSV has columns: time, event, feature1, feature2, feature3 (20 rows of data).

Use scikit-survival to fit the Cox model. Write to `/root/output.txt`:
```
Concordance index: X.XXXX
```

Round to 4 decimal places.