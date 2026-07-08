using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IPitchService
    {
        Task<ApiResponse<PitchDto>> UploadPitchAsync(UploadPitchRequest request, Guid uploadedBy);
        Task<ApiResponse<PitchDto>> UploadPitchWithFileAsync(UploadPitchRequest request, System.IO.Stream fileStream, string fileName, string contentType, long size, Guid uploadedBy, string storagePath);
        Task<ApiResponse<PitchDto>> GetPitchAsync(Guid id);
        Task<ApiResponse<IEnumerable<PitchDto>>> GetAllPitchesAsync();
        Task<ApiResponse<IEnumerable<PitchDto>>> GetPitchesByStartupAsync(Guid startupId);
    }
}
