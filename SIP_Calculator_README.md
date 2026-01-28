
# SIP Calculator - README

## Overview
This Python script is a comprehensive SIP (Systematic Investment Plan) calculator designed to help users plan their investments, project future corpus, and simulate retirement withdrawals. It supports three main modes:
- **Classic SIP Projection**: Projects the future value of SIP investments.
- **Goal-Based SIP Calculation**: Determines the required monthly SIP to reach a target corpus.
- **Timeline-Based SIP Calculation**: Calculates the number of years required to reach a target corpus with a given monthly SIP.

## Features
- **Future Value Calculation**: Projects the future value of SIP investments with step-up options.
- **Inflation Adjustment**: Adjusts returns for inflation to show real value.
- **Retirement Simulation**: Simulates withdrawals during retirement.
- **Detailed Reports**: Generates yearly and monthly breakdowns, inflation-adjusted values, and retirement projections.

## Functions

### Helper Functions

#### `CalculateReturns(Cashflows, Dates, MaxIterations=200, Precision=1e-6)`
- **Purpose**: Calculates the internal rate of return (IRR) for a series of cash flows.
- **Parameters**:
  - `Cashflows`: List of cash inflows/outflows.
  - `Dates`: List of dates corresponding to each cash flow.
  - `MaxIterations`: Maximum number of iterations for convergence.
  - `Precision`: Desired precision for the result.
- **Returns**: The calculated IRR as a percentage.

#### `CalculateInflationAdjustedReturns(Cashflows, Dates, InflationRate)`
- **Purpose**: Adjusts returns for inflation to calculate the real rate of return.
- **Parameters**:
  - `Cashflows`: List of cash inflows/outflows.
  - `Dates`: List of dates corresponding to each cash flow.
  - `InflationRate`: Annual inflation rate.
- **Returns**: The inflation-adjusted IRR as a percentage.

#### `CalculateFutureValue(MonthlyAmount, YearlyReturnPercent, InvestmentYears, YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent, StartingLumpsum=0.0)`
- **Purpose**: Calculates the future value of SIP investments.
- **Parameters**:
  - `MonthlyAmount`: Monthly investment amount.
  - `YearlyReturnPercent`: Expected annual return percentage.
  - `InvestmentYears`: Number of years for investment.
  - `YearlyIncreasePercent`: Annual increase in SIP amount.
  - `FundExpensePercent`: Fund expense ratio.
  - `TaxImpactPercent`: Tax impact on gains.
  - `StartingLumpsum`: Initial lumpsum investment.
- **Returns**: The future value of the investment.

#### `FindRequiredMonthlySip(TargetAmount, YearlyReturnPercent, InvestmentYears, YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent, StartingLumpsum=0.0)`
- **Purpose**: Determines the required monthly SIP to reach a target corpus.
- **Parameters**:
  - `TargetAmount`: Target corpus amount.
  - `YearlyReturnPercent`: Expected annual return percentage.
  - `InvestmentYears`: Number of years for investment.
  - `YearlyIncreasePercent`: Annual increase in SIP amount.
  - `FundExpensePercent`: Fund expense ratio.
  - `TaxImpactPercent`: Tax impact on gains.
  - `StartingLumpsum`: Initial lumpsum investment.
- **Returns**: The required monthly SIP amount.

#### `FindRequiredYears(TargetAmount, MonthlyAmount, YearlyReturnPercent, YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent, StartingLumpsum=0.0)`
- **Purpose**: Calculates the number of years required to reach a target corpus with a given monthly SIP.
- **Parameters**:
  - `TargetAmount`: Target corpus amount.
  - `MonthlyAmount`: Monthly investment amount.
  - `YearlyReturnPercent`: Expected annual return percentage.
  - `YearlyIncreasePercent`: Annual increase in SIP amount.
  - `FundExpensePercent`: Fund expense ratio.
  - `TaxImpactPercent`: Tax impact on gains.
  - `StartingLumpsum`: Initial lumpsum investment.
- **Returns**: The required number of years.

#### `SimulateRetirementWithdrawals(RetirementCorpus, YearlyWithdrawalPercent, InflationPercent, ReturnAfterRetirementPercent=7.0, MaxYears=40)`
- **Purpose**: Simulates withdrawals during retirement.
- **Parameters**:
  - `RetirementCorpus`: Corpus at retirement.
  - `YearlyWithdrawalPercent`: Annual withdrawal percentage.
  - `InflationPercent`: Annual inflation rate.
  - `ReturnAfterRetirementPercent`: Expected return after retirement.
  - `MaxYears`: Maximum number of years for simulation.
- **Returns**: A DataFrame with yearly withdrawal details and the number of years the corpus lasts.

### Core Function

#### `RunSipCalculation(MonthlyInvestment, ExpectedReturnPercent, InvestmentYears, FundExpenseRatio, YearlyStepUp, InflationRate, TaxOnGains, StartingLumpsum, WithdrawalRateInRetirement, ReturnAfterRetirement, OutputFile, ModeTitle="SIP CALCULATOR RESULTS")`
- **Purpose**: Runs the SIP calculation and generates detailed reports.
- **Parameters**:
  - `MonthlyInvestment`: Monthly investment amount.
  - `ExpectedReturnPercent`: Expected annual return percentage.
  - `InvestmentYears`: Number of years for investment.
  - `FundExpenseRatio`: Fund expense ratio.
  - `YearlyStepUp`: Annual increase in SIP amount.
  - `InflationRate`: Annual inflation rate.
  - `TaxOnGains`: Tax impact on gains.
  - `StartingLumpsum`: Initial lumpsum investment.
  - `WithdrawalRateInRetirement`: Annual withdrawal percentage during retirement.
  - `ReturnAfterRetirement`: Expected return after retirement.
  - `OutputFile`: Path to save the Excel report.
  - `ModeTitle`: Title for the calculation mode.
- **Returns**: A dictionary with summary, yearly progress, inflation-adjusted progress, monthly breakdown, and retirement data.

### Entry Points

#### `SimpleSipCalculator(MonthlyInvestment=10000, ExpectedReturnPercent=12.0, InvestmentYears=20, FundExpenseRatio=0.5, YearlyStepUp=10.0, InflationRate=6.0, TaxOnGains=0.0, StartingLumpsum=0.0, WithdrawalRateInRetirement=4.0, ReturnAfterRetirement=7.0, OutputFile="SIP_Calculator_Results.xlsx")`
- **Purpose**: Runs a classic SIP projection.
- **Parameters**: Same as `RunSipCalculation`.
- **Returns**: Results of the SIP calculation.

#### `GoalBaseSipCalculator(MonthlyInvestment=10000, ExpectedReturnPercent=12.0, InvestmentYears=20, FundExpenseRatio=0.5, YearlyStepUp=10.0, InflationRate=6.0, TaxOnGains=0.0, StartingLumpsum=0.0, TargetCorpus=None, SolveFor="sip", WithdrawalRateInRetirement=4.0, ReturnAfterRetirement=7.0, OutputFile="Goal_Based_SIP.xlsx")`
- **Purpose**: Determines the required monthly SIP to reach a target corpus.
- **Parameters**: Same as `RunSipCalculation`, plus:
  - `TargetCorpus`: Target corpus amount.
  - `SolveFor`: What to solve for ("sip" or "years").
- **Returns**: Results of the SIP calculation.

#### `TimeLineBaseSipCalculator(MonthlyInvestment=10000, ExpectedReturnPercent=12.0, InvestmentYears=20, FundExpenseRatio=0.5, YearlyStepUp=10.0, InflationRate=6.0, TaxOnGains=0.0, StartingLumpsum=0.0, TargetCorpus=None, SolveFor="years", WithdrawalRateInRetirement=4.0, ReturnAfterRetirement=7.0, OutputFile="Timeline_Planning.xlsx")`
- **Purpose**: Calculates the number of years required to reach a target corpus with a given monthly SIP.
- **Parameters**: Same as `RunSipCalculation`, plus:
  - `TargetCorpus`: Target corpus amount.
  - `SolveFor`: What to solve for ("sip" or "years").
- **Returns**: Results of the SIP calculation.

## Excel Output
The script generates an Excel file with the following sheets:
- **Summary**: Key metrics and summary of the SIP calculation.
- **Yearly Progress**: Yearly breakdown of investments, gains, and corpus.
- **Real Value**: Inflation-adjusted values.
- **Monthly Details**: Monthly breakdown of investments and gains.
- **Retirement**: Retirement withdrawal simulation.

## Usage
1. **Classic SIP Projection**:
   ```python
   SimpleSipCalculator(
       MonthlyInvestment=10000,
       ExpectedReturnPercent=12.0,
       InvestmentYears=20,
       OutputFile="SIP_Calculator_Results.xlsx"
   )
   ```

2. **Goal-Based SIP Calculation**:
   ```python
   GoalBaseSipCalculator(
       TargetCorpus=5000000,
       OutputFile="Goal_Based_SIP.xlsx"
   )
   ```

3. **Timeline-Based SIP Calculation**:
   ```python
   TimeLineBaseSipCalculator(
       TargetCorpus=10000000,
       OutputFile="Timeline_Planning.xlsx"
   )
   ```

## Notes
- Ensure all input parameters are realistic and within expected ranges.
- The script provides warnings for optimistic returns, high expense ratios, and unsustainable step-ups.
- The Excel output is saved to the specified path.
