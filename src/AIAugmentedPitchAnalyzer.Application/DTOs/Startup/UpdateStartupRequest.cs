using AIAugmentedPitchAnalyzer.Domain.Enums;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Startup
{
    public class UpdateStartupRequest
    {
        public string? Name { get; set; }
        public string? FounderName { get; set; }
        public string? FounderEmail { get; set; }
        public Industry? Industry { get; set; }
        public int? FundingStage { get; set; }
        public string? BusinessDescription { get; set; }
        public string? WebsiteUrl { get; set; }
    }
}
