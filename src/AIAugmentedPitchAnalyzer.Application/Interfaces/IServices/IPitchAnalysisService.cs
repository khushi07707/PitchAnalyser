using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using System;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IPitchAnalysisService
    {
        Task<ApiResponse<PitchAnalysisResultDto>> AnalyzePitchAsync(Guid pitchId, Guid requestedBy);
        Task<ApiResponse<PitchAnalysisDto>> GetPitchAnalysisAsync(Guid pitchId);
        Task<ApiResponse<PitchAnalysisParsedDto>> GetParsedPitchAnalysisAsync(Guid pitchId);
    }
}
