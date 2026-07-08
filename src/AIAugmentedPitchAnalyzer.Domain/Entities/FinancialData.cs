using System;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Optional financial dataset provided by the founder.
    /// </summary>
    public class FinancialData : BaseEntity
    {
        public Guid StartupId { get; set; }
        public Startup? Startup { get; set; }

        public decimal? AnnualRevenue { get; set; }
        public decimal? AnnualExpenses { get; set; }
        public decimal? NetProfit { get; set; }
        public string? Currency { get; set; }
        public int? FiscalYear { get; set; }
    }
}
