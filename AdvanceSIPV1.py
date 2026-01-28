import pandas as pd
from datetime import datetime, timedelta
import numpy as np


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def CalculateReturns(Cashflows, Dates, MaxIterations=200, Precision=1e-6):
    if len(Cashflows) != len(Dates):
        raise ValueError("Number of cashflows must match number of dates")

    TotalInvested = sum(cf for cf in Cashflows if cf < 0)
    FinalValue = sum(cf for cf in Cashflows if cf > 0)
    
    if TotalInvested == 0 or FinalValue == 0:
        return 0.0

    Years = (Dates[-1] - Dates[0]).days / 365.25
    InitialGuess = (FinalValue / abs(TotalInvested)) ** (1 / Years) - 1 if Years > 0 else 0.1

    def CalculateNetPresentValue(Rate):
        return sum(
            cf / ((1 + Rate) ** ((d - Dates[0]).days / 365.25))
            for cf, d in zip(Cashflows, Dates)
        )

    Rate = max(-0.99, min(InitialGuess, 5.0))
    for _ in range(MaxIterations):
        Npv = CalculateNetPresentValue(Rate)
        if abs(Npv) < Precision:
            return Rate * 100
        
        Derivative = (CalculateNetPresentValue(Rate + 1e-6) - Npv) / 1e-6
        if abs(Derivative) < 1e-10:
            break
        Rate -= Npv / Derivative

    Low, High = -0.99, 5.0
    for _ in range(MaxIterations):
        Mid = (Low + High) / 2
        MidNpv = CalculateNetPresentValue(Mid)
        if abs(MidNpv) < Precision:
            return Mid * 100
        if MidNpv * CalculateNetPresentValue(Low) > 0:
            Low = Mid
        else:
            High = Mid
    
    return Mid * 100


def CalculateInflationAdjustedReturns(Cashflows, Dates, InflationRate):
    AdjustedCashflows = []
    StartDate = Dates[0]
    
    for cf, d in zip(Cashflows, Dates):
        Years = (d - StartDate).days / 365.25
        # For outflows (negative cf): we pay more in future rupees → inflate the outflow
        # For inflows (positive cf): future money worth less today → deflate the inflow
        if cf < 0:
            adjusted_cf = cf * (1 + InflationRate) ** Years     # outflow becomes larger in today's terms
        else:
            adjusted_cf = cf / (1 + InflationRate) ** Years     # inflow becomes smaller in today's terms
        AdjustedCashflows.append(adjusted_cf)
    
    return CalculateReturns(AdjustedCashflows, Dates)  # now solves for real rate


def CalculateFutureValue(
    MonthlyAmount, YearlyReturnPercent, InvestmentYears,
    YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent,
    StartingLumpsum=0.0
):
    NetReturn = YearlyReturnPercent - FundExpensePercent - TaxImpactPercent
    if NetReturn <= 0:
        return 0.0
    
    AnnualRate = NetReturn / 100
    MonthlyRate = (1 + AnnualRate) ** (1 / 12) - 1
    TotalMonths = int(InvestmentYears * 12)
    
    if TotalMonths == 0:
        return StartingLumpsum

    FutureValue = StartingLumpsum * (1 + MonthlyRate) ** TotalMonths
    MonthlySip = MonthlyAmount
    
    for Month in range(TotalMonths):
        MonthsRemaining = TotalMonths - Month
        FutureValue += MonthlySip * (1 + MonthlyRate) ** MonthsRemaining
        
        if (Month + 1) % 12 == 0 and Month < TotalMonths - 1:
            MonthlySip *= (1 + YearlyIncreasePercent / 100)

    return FutureValue


def FindRequiredMonthlySip(
    TargetAmount, YearlyReturnPercent, InvestmentYears,
    YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent,
    StartingLumpsum=0.0
):
    Low, High = 0, TargetAmount * 2
    for _ in range(100):
        Mid = (Low + High) / 2
        if CalculateFutureValue(
            Mid, YearlyReturnPercent, InvestmentYears,
            YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent,
            StartingLumpsum
        ) < TargetAmount:
            Low = Mid
        else:
            High = Mid
    return round(Mid, 0)


def FindRequiredYears(
    TargetAmount, MonthlyAmount, YearlyReturnPercent,
    YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent,
    StartingLumpsum=0.0
):
    Low, High = 0.1, 80
    for _ in range(100):
        Mid = (Low + High) / 2
        if CalculateFutureValue(
            MonthlyAmount, YearlyReturnPercent, Mid,
            YearlyIncreasePercent, FundExpensePercent, TaxImpactPercent,
            StartingLumpsum
        ) < TargetAmount:
            Low = Mid
        else:
            High = Mid
    return round(Mid, 1)


def SimulateRetirementWithdrawals(
    RetirementCorpus, YearlyWithdrawalPercent, InflationPercent,
    ReturnAfterRetirementPercent=7.0, MaxYears=40
):
    WithdrawalRate = YearlyWithdrawalPercent / 100
    Inflation = InflationPercent / 100
    InvestmentReturn = ReturnAfterRetirementPercent / 100

    FirstYearWithdrawal = RetirementCorpus * WithdrawalRate
    RemainingCorpus = RetirementCorpus
    YearlyData = []
    YearsMoneyLasts = 0

    for Year in range(1, MaxYears + 1):
        AnnualWithdrawal = FirstYearWithdrawal * (1 + Inflation) ** (Year - 1)
        CorpusStart = RemainingCorpus
        RemainingCorpus = RemainingCorpus * (1 + InvestmentReturn) - AnnualWithdrawal
        
        YearlyData.append({
            "Year": Year,
            "Withdrawal Amount": round(AnnualWithdrawal, 0),
            "Corpus at Year Start": round(CorpusStart, 0),
            "Corpus at Year End": round(max(RemainingCorpus, 0), 0),
            "Withdrawal as % of Corpus": round((AnnualWithdrawal / CorpusStart * 100), 2) if CorpusStart > 0 else 0,
        })
        
        if RemainingCorpus > 0:
            YearsMoneyLasts = Year
        else:
            break

    return pd.DataFrame(YearlyData), YearsMoneyLasts


# ═══════════════════════════════════════════════════════════════════
# CORE CALCULATION (shared by all modes)
# ═══════════════════════════════════════════════════════════════════

def RunSipCalculation(
    MonthlyInvestment,
    ExpectedReturnPercent,
    InvestmentYears,
    FundExpenseRatio,
    YearlyStepUp,
    InflationRate,
    TaxOnGains,
    StartingLumpsum,
    WithdrawalRateInRetirement,
    ReturnAfterRetirement,
    OutputFile,
    ModeTitle="SIP CALCULATOR RESULTS"
):
    if InvestmentYears <= 0:
        raise ValueError("Investment period must be positive")
    if MonthlyInvestment < 0:
        raise ValueError("Monthly investment cannot be negative")
    if StartingLumpsum < 0:
        raise ValueError("Starting lumpsum cannot be negative")

    NetReturn = ExpectedReturnPercent - FundExpenseRatio - TaxOnGains
    if NetReturn <= 0:
        raise ValueError(f"Net return ({NetReturn:.2f}%) must be positive!")

    # Warnings
    if ExpectedReturnPercent > 20:
        print(f"⚠️  WARNING: {ExpectedReturnPercent}% return is very optimistic.")
    if YearlyStepUp > 25:
        print(f"⚠️  WARNING: {YearlyStepUp}% yearly step-up may be unsustainable.")
    if FundExpenseRatio > 2.5:
        print(f"⚠️  WARNING: {FundExpenseRatio}% expense ratio is high.")

    YearlyReturn = NetReturn / 100
    MonthlyReturn = (1 + YearlyReturn) ** (1 / 12) - 1
    InflationMultiplier = InflationRate / 100
    StepUpMultiplier = YearlyStepUp / 100
    TotalMonths = int(InvestmentYears * 12)

    # Final Corpus
    FinalCorpus = StartingLumpsum * (1 + MonthlyReturn) ** TotalMonths if TotalMonths > 0 else StartingLumpsum
    TotalAmountInvested = StartingLumpsum
    TotalStepUpAmount = 0.0
    MonthlySip = MonthlyInvestment

    for Month in range(TotalMonths):
        MonthsRemaining = TotalMonths - Month
        FinalCorpus += MonthlySip * (1 + MonthlyReturn) ** MonthsRemaining
        TotalAmountInvested += MonthlySip
        
        if (Month + 1) % 12 == 0 and Month < TotalMonths - 1:
            StepUpThisYear = MonthlySip * StepUpMultiplier * 12
            TotalStepUpAmount += StepUpThisYear
            MonthlySip *= (1 + StepUpMultiplier)

    TotalGains = FinalCorpus - TotalAmountInvested
    RealCorpus = FinalCorpus / (1 + InflationMultiplier) ** InvestmentYears if InvestmentYears > 0 else FinalCorpus
    InflationLoss = FinalCorpus - RealCorpus

    # XIRR
    Cashflows = [-StartingLumpsum]
    Dates = [datetime.today()]
    CurrentSip = MonthlyInvestment
    CurrentDate = Dates[0]

    for Month in range(TotalMonths):
        CurrentDate += timedelta(days=30.4375)
        Dates.append(CurrentDate)
        Cashflows.append(-CurrentSip)
        
        if (Month + 1) % 12 == 0 and Month < TotalMonths - 1:
            CurrentSip *= (1 + StepUpMultiplier)

    CurrentDate += timedelta(days=30.4375)
    Dates.append(CurrentDate)
    Cashflows.append(FinalCorpus)

    ActualReturnXirr = CalculateReturns(Cashflows, Dates)
    RealReturnXirr = CalculateInflationAdjustedReturns(Cashflows, Dates, InflationMultiplier)

    SimpleCagr = (
        ((FinalCorpus / TotalAmountInvested) ** (1 / InvestmentYears) - 1) * 100
        if TotalAmountInvested > 0 and InvestmentYears > 0 else 0
    )

    # Detailed Progress Tables
    YearlyProgress = []
    InflationAdjustedProgress = []
    MonthlyBreakdown = []

    CurrentBalance = StartingLumpsum
    TotalInvestedSoFar = StartingLumpsum
    CurrentSip = MonthlyInvestment
    CumulativeGains = 0.0
    GainsExceedInvestmentYear = None
    GainsExceedInvestmentMonth = None

    for MonthNum in range(TotalMonths):
        Year = (MonthNum // 12) + 1
        MonthInYear = (MonthNum % 12) + 1
        
        MonthlyGain = CurrentBalance * MonthlyReturn
        CurrentBalance += MonthlyGain
        CurrentBalance += CurrentSip
        TotalInvestedSoFar += CurrentSip
        CumulativeGains += MonthlyGain

        MonthlyBreakdown.append({
            "Year": Year,
            "Month": MonthInYear,
            "SIP Amount": round(CurrentSip, 0),
            "Balance Before SIP": round(CurrentBalance - CurrentSip, 0),
            "Monthly Gain": round(MonthlyGain, 0),
            "Balance After SIP": round(CurrentBalance, 0),
            "Total Invested So Far": round(TotalInvestedSoFar, 0),
            "Total Gains So Far": round(CumulativeGains, 0),
        })

        if CumulativeGains > TotalInvestedSoFar and GainsExceedInvestmentYear is None:
            GainsExceedInvestmentYear = Year
            GainsExceedInvestmentMonth = MonthInYear

        if MonthInYear == 12 or MonthNum == TotalMonths - 1:
            YearStartBalance = StartingLumpsum if Year == 1 else YearlyProgress[-1]["Balance at Year End"]
            
            InvestedThisYear = sum(
                row["SIP Amount"] for row in MonthlyBreakdown if row["Year"] == Year
            )
            GainsThisYear = sum(
                row["Monthly Gain"] for row in MonthlyBreakdown if row["Year"] == Year
            )
            
            WealthMultiplier = CurrentBalance / TotalInvestedSoFar if TotalInvestedSoFar > 0 else 0
            GainsToInvestmentRatio = (CurrentBalance - TotalInvestedSoFar) / TotalInvestedSoFar if TotalInvestedSoFar > 0 else 0
            
            if GainsToInvestmentRatio < 1:
                WealthPhase = "📊 Building Phase"
                PhaseDescription = "Your contributions drive growth"
            elif GainsToInvestmentRatio < 3:
                WealthPhase = "⚡ Acceleration Phase"
                PhaseDescription = "Compounding kicks in"
            else:
                WealthPhase = "🚀 Compounding Phase"
                PhaseDescription = "Returns drive most growth"

            YearlyProgress.append({
                "Year": Year,
                "Starting SIP": round(MonthlyInvestment * (1 + StepUpMultiplier) ** (Year - 1), 0),  # FIXED LINE
                "Invested This Year": round(InvestedThisYear, 0),
                "Total Invested": round(TotalInvestedSoFar, 0),
                "Balance at Year Start": round(YearStartBalance, 0),
                "Gains This Year": round(GainsThisYear, 0),
                "Balance at Year End": round(CurrentBalance, 0),
                "Total Gains": round(CumulativeGains, 0),
                "Wealth Multiplier": round(WealthMultiplier, 2),
                "Gains/Investment Ratio": round(GainsToInvestmentRatio, 2),
                "Yearly Return %": round((CurrentBalance / TotalInvestedSoFar - 1) * 100, 2) if TotalInvestedSoFar > 0 else 0,
                "Rolling CAGR %": round(((CurrentBalance / TotalInvestedSoFar) ** (1 / Year) - 1) * 100, 2) if TotalInvestedSoFar > 0 else 0,
                "Wealth Phase": WealthPhase,
                "Phase Description": PhaseDescription,
                "Compounding Milestone": "✅ Yes" if GainsExceedInvestmentYear == Year else "",
            })

            RealBalance = CurrentBalance / (1 + InflationMultiplier) ** Year if Year > 0 else CurrentBalance
            RealInvested = TotalInvestedSoFar / (1 + InflationMultiplier) ** Year if Year > 0 else TotalInvestedSoFar
            
            InflationAdjustedProgress.append({
                "Year": Year,
                "Real Balance (Today's Value)": round(RealBalance, 0),
                "Real Invested (Today's Value)": round(RealInvested, 0),
                "Real Gains": round(RealBalance - RealInvested, 0),
                "Real Wealth Multiplier": round(RealBalance / RealInvested, 2) if RealInvested > 0 else 0,
                "Real CAGR %": round(((RealBalance / RealInvested) ** (1 / Year) - 1) * 100, 2) if RealInvested > 0 and Year > 0 else 0,
                "Inflation Loss This Year": round(GainsThisYear * InflationMultiplier, 0),
                "Cumulative Inflation Loss": round(CurrentBalance - RealBalance, 0),
                "Purchasing Power vs Invested": f"{round((RealBalance / RealInvested) * 100, 0)}%" if RealInvested > 0 else "0%",
            })
        
        if MonthInYear == 12 and MonthNum < TotalMonths - 1:
            CurrentSip *= (1 + StepUpMultiplier)

    # Retirement simulation
    RetirementData, YearsCorpusLasts = SimulateRetirementWithdrawals(
        CurrentBalance,
        WithdrawalRateInRetirement,
        InflationRate,
        ReturnAfterRetirement
    )

    # Summary
    MilestoneText = f"Year {GainsExceedInvestmentYear}, Month {GainsExceedInvestmentMonth}" if GainsExceedInvestmentYear else "Not reached yet"
    
    Summary = {
        "💰 Total Amount Invested": f"₹{TotalAmountInvested:,.0f}",
        "🎯 Final Corpus": f"₹{FinalCorpus:,.0f}",
        "📈 Total Gains": f"₹{TotalGains:,.0f}",
        "🔢 Wealth Multiplier": f"{round(FinalCorpus / TotalAmountInvested, 2)}x" if TotalAmountInvested > 0 else "0x",
        "": "",
        "💵 Starting Lumpsum": f"₹{StartingLumpsum:,.0f}",
        "📊 Total SIP Invested": f"₹{TotalAmountInvested - StartingLumpsum:,.0f}",
        "⬆️  Total Step-up Amount": f"₹{TotalStepUpAmount:,.0f}",
        " ": "",
        "📉 Expected Return": f"{ExpectedReturnPercent}%",
        "💸 Fund Expense Ratio": f"{FundExpenseRatio}%",
        "🏛️ Tax Impact": f"{TaxOnGains}%",
        "✅ Net Return": f"{NetReturn}%",
        "  ": "",
        "📊 CAGR": f"{round(SimpleCagr, 2)}%",
        "💹 Actual Return (XIRR)": f"{round(ActualReturnXirr, 2)}%",
        "💰 Real Return (After Inflation)": f"{round(RealReturnXirr, 2)}%",
        "   ": "",
        "🌾 Inflation Rate": f"{InflationRate}%",
        "🏠 Real Corpus (Today's Value)": f"₹{RealCorpus:,.0f}",
        "📉 Inflation Loss": f"₹{InflationLoss:,.0f}",
        "    ": "",
        "🎯 Compounding Milestone": MilestoneText,
        "⏱️  Years Corpus Lasts (@ {:.1f}% withdrawal)".format(WithdrawalRateInRetirement): f"{YearsCorpusLasts} years",
    }

    # Print summary
    print("\n" + "═" * 60)
    print(f"📊 {ModeTitle}")
    print("═" * 60)
    
    for Key, Value in Summary.items():
        if Key.strip():
            print(f"{Key:45} : {Value}")
    
    print("\n💾 Saving detailed results to Excel...")

    # Save to Excel
    with pd.ExcelWriter(OutputFile, engine="openpyxl") as Writer:
        pd.DataFrame(list(Summary.items()), columns=["Metric", "Value"]).to_excel(Writer, sheet_name="📊 Summary", index=False)
        pd.DataFrame(YearlyProgress).to_excel(Writer, sheet_name="📈 Yearly Progress", index=False)
        pd.DataFrame(InflationAdjustedProgress).to_excel(Writer, sheet_name="💰 Real Value", index=False)
        pd.DataFrame(MonthlyBreakdown).to_excel(Writer, sheet_name="📅 Monthly Details", index=False)
        RetirementData.to_excel(Writer, sheet_name="🏖️ Retirement", index=False)

    print(f"✅ Results saved to: {OutputFile}")
    print("═" * 60 + "\n")

    return {
        "summary": Summary,
        "yearly_progress": YearlyProgress,
        "inflation_adjusted": InflationAdjustedProgress,
        "monthly_breakdown": MonthlyBreakdown,
        "retirement_data": RetirementData,
    }


# ═══════════════════════════════════════════════════════════════════
# CALCULATOR ENTRY POINTS
# ═══════════════════════════════════════════════════════════════════

def SimpleSipCalculator(
    MonthlyInvestment=10000,
    ExpectedReturnPercent=12.0,
    InvestmentYears=20,
    FundExpenseRatio=0.5,
    YearlyStepUp=10.0,
    InflationRate=6.0,
    TaxOnGains=0.0,
    StartingLumpsum=0.0,
    WithdrawalRateInRetirement=4.0,
    ReturnAfterRetirement=7.0,
    OutputFile="SIP_Calculator_Results.xlsx"
):
    print("\nRunning → Classic SIP Projection")
    return RunSipCalculation(
        MonthlyInvestment, ExpectedReturnPercent, InvestmentYears,
        FundExpenseRatio, YearlyStepUp, InflationRate, TaxOnGains,
        StartingLumpsum, WithdrawalRateInRetirement, ReturnAfterRetirement,
        OutputFile, "CLASSIC SIP PROJECTION"
    )


def GoalBaseSipCalculator(
    MonthlyInvestment=10000,
    ExpectedReturnPercent=12.0,
    InvestmentYears=20,
    FundExpenseRatio=0.5,
    YearlyStepUp=10.0,
    InflationRate=6.0,
    TaxOnGains=0.0,
    StartingLumpsum=0.0,
    TargetCorpus=None,
    SolveFor="sip",
    WithdrawalRateInRetirement=4.0,
    ReturnAfterRetirement=7.0,
    OutputFile="Goal_Based_SIP.xlsx"
):
    if TargetCorpus is None or TargetCorpus <= 0:
        raise ValueError("TargetCorpus is required and must be > 0")

    RequiredMonthly = FindRequiredMonthlySip(
        TargetCorpus, ExpectedReturnPercent, InvestmentYears,
        YearlyStepUp, FundExpenseRatio, TaxOnGains, StartingLumpsum
    )

    print(f"\nTo reach ₹{TargetCorpus:,.0f} in {InvestmentYears} years → invest ₹{RequiredMonthly:,.0f}/month")
    print(f"   (with {YearlyStepUp}% yearly step-up)\n")

    return RunSipCalculation(
        RequiredMonthly, ExpectedReturnPercent, InvestmentYears,
        FundExpenseRatio, YearlyStepUp, InflationRate, TaxOnGains,
        StartingLumpsum, WithdrawalRateInRetirement, ReturnAfterRetirement,
        OutputFile, "GOAL BASED SIP CALCULATION"
    )


def TimeLineBaseSipCalculator(
    MonthlyInvestment=10000,
    ExpectedReturnPercent=12.0,
    InvestmentYears=20,
    FundExpenseRatio=0.5,
    YearlyStepUp=10.0,
    InflationRate=6.0,
    TaxOnGains=0.0,
    StartingLumpsum=0.0,
    TargetCorpus=None,
    SolveFor="years",
    WithdrawalRateInRetirement=4.0,
    ReturnAfterRetirement=7.0,
    OutputFile="Timeline_Planning.xlsx"
):
    if TargetCorpus is None or TargetCorpus <= 0:
        raise ValueError("TargetCorpus is required and must be > 0")

    RequiredYears = FindRequiredYears(
        TargetCorpus, MonthlyInvestment, ExpectedReturnPercent,
        YearlyStepUp, FundExpenseRatio, TaxOnGains, StartingLumpsum
    )

    print(f"\nTo reach ₹{TargetCorpus:,.0f} with ₹{MonthlyInvestment:,.0f}/month → need ≈ {RequiredYears} years")
    print(f"   (with {YearlyStepUp}% yearly step-up)\n")

    return RunSipCalculation(
        MonthlyInvestment, ExpectedReturnPercent, RequiredYears,
        FundExpenseRatio, YearlyStepUp, InflationRate, TaxOnGains,
        StartingLumpsum, WithdrawalRateInRetirement, ReturnAfterRetirement,
        OutputFile, "TIMELINE BASED SIP CALCULATION"
    )


# ═══════════════════════════════════════════════════════════════════
# EXAMPLES
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    Path = r"C:\Users\Vatsal\Document\VSCodeFiles\PythonCode\FinancialCalculator\Data"

    print("\n🔹 EXAMPLE 1: Basic SIP Calculation")
    SimpleSipCalculator(
        MonthlyInvestment=10000,
        ExpectedReturnPercent=12.0,
        InvestmentYears=20,
        FundExpenseRatio=0.5,
        YearlyStepUp=10.0,
        InflationRate=6.0,
        StartingLumpsum=50000,
        OutputFile=f"{Path}\\Basic_SIP_Example.xlsx",
    )

    print("\n🔹 EXAMPLE 2: Goal Planning - Find Required SIP")
    GoalBaseSipCalculator(
        MonthlyInvestment=10000,
        ExpectedReturnPercent=12.0,
        InvestmentYears=20,
        FundExpenseRatio=0.5,
        YearlyStepUp=10.0,
        InflationRate=6.0,
        TargetCorpus=5000000,
        OutputFile=f"{Path}\\Goal_Based_SIP.xlsx",
    )

    print("\n🔹 EXAMPLE 3: Goal Planning - Find Required Years")
    TimeLineBaseSipCalculator(
        MonthlyInvestment=10000,
        ExpectedReturnPercent=12.0,
        InvestmentYears=20,
        FundExpenseRatio=0.5,
        YearlyStepUp=10.0,
        InflationRate=6.0,
        TargetCorpus=10000000,
        OutputFile=f"{Path}\\Timeline_Planning.xlsx",
    )