using AIAugmentedPitchAnalyzer.Domain.Enums;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Startup
{
    public class CreateStartupRequest
    {
        public string Name { get; set; } = null!;
        public string FounderName { get; set; } = null!;
        public string FounderEmail { get; set; } = null!;
        public Industry Industry { get; set; }
        public int FundingStage { get; set; }
        public string BusinessDescription { get; set; } = null!;
        public string? WebsiteUrl { get; set; }
    }
}
