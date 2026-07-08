using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class PitchAnalysisResultDto
    {
        public Guid PitchId { get; set; }
        public string Summary { get; set; } = null!;
        public double Score { get; set; }
        public string Recommendations { get; set; } = null!;
        public string AnalysisJson { get; set; } = null!;
        public DateTime? CompletedAt { get; set; }
    }
}
