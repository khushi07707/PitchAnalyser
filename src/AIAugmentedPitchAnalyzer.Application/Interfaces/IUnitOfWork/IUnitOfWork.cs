using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Application.Interfaces.IUnitOfWork
{
    public interface IUnitOfWork
    {
        Task<int> SaveChangesAsync();
    }
}
