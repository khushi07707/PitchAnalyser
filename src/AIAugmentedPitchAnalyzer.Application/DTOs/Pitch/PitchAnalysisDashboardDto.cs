using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class PitchAnalysisDashboardDto
    {
        public int TotalPitches { get; set; }
        public int AnalyzedPitches { get; set; }
        public int PendingAnalysis { get; set; }
        public double AverageScore { get; set; }
        public double HighestScore { get; set; }
        public double LowestScore { get; set; }
    }
}
