using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Persistence.Repositories;
using AIAugmentedPitchAnalyzer.Persistence.UnitOfWork;
using AIAugmentedPitchAnalyzer.Infrastructure.Services;
using Microsoft.Extensions.DependencyInjection;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Extensions
{
    /// <summary>
    /// Registers infrastructure and persistence services into DI container.
    /// Call from `Program.cs` in the API project.
    /// </summary>
    public static class ServiceCollectionExtensions
    {
        public static IServiceCollection AddInfrastructure(this IServiceCollection services)
        {
            services.AddScoped(typeof(IGenericRepository<>), typeof(GenericRepository<>));
            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IStartupRepository, StartupRepository>();
            services.AddScoped<IPitchRepository, PitchRepository>();

            services.AddScoped<IUnitOfWork, UnitOfWork>();

            services.AddScoped<IAuthService, AuthService>();
            services.AddScoped<ITokenService, TokenService>();
            services.AddScoped<IStartupService, StartupService>();
            services.AddScoped<IPitchService, PitchService>();
            services.AddScoped<IPitchAnalysisService, PitchAnalysisService>();
            services.AddScoped<IPromptBuilder, PromptBuilder>();
            services.AddScoped<IFileService, FileService>();
            services.AddScoped<ITextExtractionService, TextExtractionService>();

            return services;
        }
    }
}
