using System.Collections.Generic;
using AIAugmentedPitchAnalyzer.Domain.Enums;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Represents a startup submitted by a founder.
    /// </summary>
    public class Startup : BaseEntity
    {
        public string Name { get; set; } = null!;
        public string FounderName { get; set; } = null!;
        public string FounderEmail { get; set; } = null!;
        public Industry Industry { get; set; } = Industry.Other;
        public FundingStage FundingStage { get; set; } = FundingStage.Unknown;
        public string BusinessDescription { get; set; } = null!;
        public string? WebsiteUrl { get; set; }

        public Guid CreatedById { get; set; }
        public User? CreatedBy { get; set; }

        public FinancialData? FinancialData { get; set; }
        public ICollection<Pitch>? Pitches { get; set; }
    }
}
