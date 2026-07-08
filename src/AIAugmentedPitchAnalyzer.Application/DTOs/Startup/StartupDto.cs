using System;
using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
using AIAugmentedPitchAnalyzer.Domain.Enums;
using System.Collections.Generic;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Startup
{
    public class StartupDto
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = null!;
        public string FounderName { get; set; } = null!;
        public string FounderEmail { get; set; } = null!;
        public Industry Industry { get; set; }
        public int FundingStage { get; set; }
        public string BusinessDescription { get; set; } = null!;
        public string? WebsiteUrl { get; set; }

        public IEnumerable<PitchDto>? Pitches { get; set; }
    }
}
