using AIAugmentedPitchAnalyzer.Application.DTOs.File;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using AutoMapper;
using System;
using System.IO;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    public class FileService : IFileService
    {
        private readonly IGenericRepository<FileRecord> _fileRepository;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;
        private readonly ITextExtractionService _textExtractionService;

        public FileService(IGenericRepository<FileRecord> fileRepository, IUnitOfWork unitOfWork, IMapper mapper, ITextExtractionService textExtractionService)
        {
            _fileRepository = fileRepository;
            _unitOfWork = unitOfWork;
            _mapper = mapper;
            _textExtractionService = textExtractionService;
        }

        public async Task<ApiResponse<FileRecordDto>> UploadFileAsync(Stream fileStream, string fileName, string contentType, long size, Guid uploadedBy, string storagePath)
        {
            try
            {
                Directory.CreateDirectory(storagePath);
                var storedFileName = $"{Guid.NewGuid()}{Path.GetExtension(fileName)}";
                var fullPath = Path.Combine(storagePath, storedFileName);

                using (var fs = File.Create(fullPath))
                {
                    await fileStream.CopyToAsync(fs);
                }

                var record = new FileRecord
                {
                    Id = Guid.NewGuid(),
                    FileName = fileName,
                    FilePath = fullPath,
                    ContentType = contentType,
                    Size = size,
                    UploadedAt = DateTime.UtcNow,
                    UploadedById = uploadedBy
                };

                await _fileRepository.AddAsync(record);
                await _unitOfWork.SaveChangesAsync();

                var dto = _mapper.Map<FileRecordDto>(record);
                return new ApiResponse<FileRecordDto> { Data = dto };
            }
            catch (Exception ex)
            {
                return new ApiResponse<FileRecordDto> { Success = false, Message = ex.Message };
            }
        }

        public async Task<ApiResponse<FileRecordDto>> GetFileAsync(Guid id)
        {
            var record = await _fileRepository.GetByIdAsync(id);
            if (record == null) return new ApiResponse<FileRecordDto> { Success = false, Message = "File not found" };
            var dto = _mapper.Map<FileRecordDto>(record);
            return new ApiResponse<FileRecordDto> { Data = dto };
        }

        public async Task<ApiResponse<string>> ExtractTextAsync(Guid fileId)
        {
            var record = await _fileRepository.GetByIdAsync(fileId);
            if (record == null)
            {
                return new ApiResponse<string> { Success = false, Message = "File not found" };
            }

            var result = await _textExtractionService.ExtractTextFromFileAsync(record.FilePath, record.ContentType);
            if (!result.Success)
            {
                return new ApiResponse<string> { Success = false, Message = result.Message };
            }

            return new ApiResponse<string> { Data = result.Data };
        }
    }
}
