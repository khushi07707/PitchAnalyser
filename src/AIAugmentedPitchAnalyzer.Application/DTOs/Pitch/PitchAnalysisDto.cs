using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class PitchAnalysisDto
    {
        public Guid Id { get; set; }
        public Guid PitchId { get; set; }
        public string AnalysisJson { get; set; } = null!;
        public string? Summary { get; set; }
        public double? Score { get; set; }
        public string? Recommendations { get; set; }
        public DateTime? CompletedAt { get; set; }
    }
}
