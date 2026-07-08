using System;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Represents an uploaded pitch for a startup.
    /// </summary>
    public class Pitch : BaseEntity
    {
        public Guid StartupId { get; set; }
        public Startup? Startup { get; set; }

        public string Title { get; set; } = "Pitch Deck";
        public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

        public Guid? FileRecordId { get; set; }
        public FileRecord? FileRecord { get; set; }

        public string? ExtractedText { get; set; }

        public PitchAnalysis? Analysis { get; set; }
    }
}
