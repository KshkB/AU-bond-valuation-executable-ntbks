# Aussie bond valuation

This repository contains Python scripts and executable (Jupyter) notebooks which generate metrics for valuing and sketching Australian Government Treasury Bonds. Specifically:

- `AU_eTB_ntbk` generates valuation metrics for exchange traded treasury bonds (eTBs);
- `AU_eTIB_ntbk` generates valuation metrics for exchange traded, *inflation protected* treasury bonds (eTIBs).

Open these notebooks, uncomment and run the code blocks to generate desired analytics.

## Requirements

See `requirements.txt` for a list of Python dependencies needed to execute the notebooks. Note, `tabula-py` is a wrapper of a Java program and needs Java installed in order to run. It is only used in the notebook `AU_eTIB_ntbk`. 

## Valuation metrics

Metrics used to value the bonds are the *bond yield* and the *net bond value*. For both eTBs and eTIBs, their yield is given by:

$$\mathrm{YIELD} = \frac{\mathrm{COUPON}}{\mathrm{PRICE}}\times\mathrm{FACEVALUE}.$$

### Valuation for eTBs

Value is determined by how much is returned in holding one eTB to maturity calculated by

$$\mathrm{VALUE} = -\mathrm{PRICE} + \left(1 + \mathrm{COUPON}\times\mathrm{MATURITY}\right)\times\mathrm{FACEVALUE},$$

where $\mathrm{MATURITY}$ is the number of coupon payment periods from the present time to the time the bond matures. 

From $\mathrm{VALUE}$ the value per coupon payment period is $\mathrm{VALUE}/\mathrm{MATURITY}$. 
The value *yield* is the return per coupon payment period in proportion to the price,

$$\mathrm{VALUEYIELD} = \frac{\mathrm{VALUE}}{\mathrm{PRICE}\times\mathrm{MATURITY}}.$$

### Valuation for eTIBs

The face value for eTIBs change each period in line with inflation.
The value for eTBs is a special case of value for the inflation protected bonds, eTIBs, with *zero* inflation. 
In general, value for eTIBs are given by

$$\mathrm{VALUE} = -\mathrm{PRICE} + \left((1 + \mathrm{INFL.})^{\mathrm{MATURITY}} + \mathrm{COUPON}\times\sum_{i=0}^{\mathrm{MATURITY-1}}(1 + \mathrm{INFL.})^i\right)\times \mathrm{FACEVALUE}.$$



