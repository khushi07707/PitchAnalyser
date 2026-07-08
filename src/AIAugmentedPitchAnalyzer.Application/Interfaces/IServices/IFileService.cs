using AIAugmentedPitchAnalyzer.Application.DTOs.File;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using System;
using System.IO;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IServices
{
    public interface IFileService
    {
        Task<ApiResponse<FileRecordDto>> UploadFileAsync(Stream fileStream, string fileName, string contentType, long size, Guid uploadedBy, string storagePath);
        Task<ApiResponse<FileRecordDto>> GetFileAsync(Guid id);
        Task<ApiResponse<string>> ExtractTextAsync(Guid fileId);
    }
}
