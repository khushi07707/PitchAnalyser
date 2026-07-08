using System;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Stores AI-generated analysis for a pitch.
    /// </summary>
    public class PitchAnalysis : BaseEntity
    {
        public Guid PitchId { get; set; }
        public Pitch? Pitch { get; set; }

        /// <summary>
        /// Raw JSON returned by the AI provider.
        /// </summary>
        public string AnalysisJson { get; set; } = null!;

        /// <summary>
        /// Short human-readable summary.
        /// </summary>
        public string? Summary { get; set; }

        /// <summary>
        /// Normalized score (0..100).
        /// </summary>
        public double? Score { get; set; }

        /// <summary>
        /// Recommendations, possibly JSON or text.
        /// </summary>
        public string? Recommendations { get; set; }

        public DateTime? CompletedAt { get; set; }
    }
}
