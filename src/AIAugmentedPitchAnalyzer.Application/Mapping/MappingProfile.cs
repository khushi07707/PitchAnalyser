using AutoMapper;
using AIAugmentedPitchAnalyzer.Application.DTOs.User;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Application.DTOs.Startup;
using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;

namespace AIAugmentedPitchAnalyzer.Application.Mapping
{
    public class MappingProfile : Profile
    {
        public MappingProfile()
        {
            CreateMap<User, UserDto>().ReverseMap();
            CreateMap<Startup, StartupDto>().ReverseMap();
            CreateMap<CreateStartupRequest, Startup>().ReverseMap();
            CreateMap<PitchAnalysis, PitchAnalysisDto>().ReverseMap();
            CreateMap<PitchAnalysis, PitchAnalysisResultDto>().ReverseMap();
            CreateMap<PitchAnalysis, PitchAnalysisParsedDto>().ReverseMap();
            CreateMap<Pitch, PitchDto>().ReverseMap();
            CreateMap<UploadPitchRequest, Pitch>().ReverseMap();
            CreateMap<Domain.Entities.FileRecord, AIAugmentedPitchAnalyzer.Application.DTOs.File.FileRecordDto>().ReverseMap();
            // Additional maps will be added as DTOs are created.
        }
    }
}
