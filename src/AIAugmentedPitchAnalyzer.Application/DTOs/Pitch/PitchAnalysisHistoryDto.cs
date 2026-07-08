using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class PitchAnalysisHistoryDto
    {
        public Guid PitchId { get; set; }
        public string PitchTitle { get; set; } = null!;
        public Guid AnalysisId { get; set; }
        public string Summary { get; set; } = null!;
        public double? Score { get; set; }
        public string? Recommendations { get; set; }
        public DateTime? CompletedAt { get; set; }
    }
}
