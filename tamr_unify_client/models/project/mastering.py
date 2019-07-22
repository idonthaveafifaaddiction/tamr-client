from tamr_unify_client.models.binning_model import BinningModel
from tamr_unify_client.models.dataset.resource import Dataset
from tamr_unify_client.models.machine_learning_model import MachineLearningModel
from tamr_unify_client.models.operation import Operation
from tamr_unify_client.models.project.cluster_configuration import (
    PublishedClustersConfiguration,
)
from tamr_unify_client.models.project.estimated_pair_counts import EstimatedPairCounts
from tamr_unify_client.models.project.resource import Project


class MasteringProject(Project):
    """A Mastering project in Unify."""

    def pairs(self):
        """Record pairs generated by Unify's binning model.
        Pairs are displayed on the "Pairs" page in the Unify UI.

        Call :func:`~tamr_unify_client.models.dataset.resource.Dataset.refresh` from
        this dataset to regenerate pairs according to the latest binning model.

        :returns: The record pairs represented as a dataset.
        :rtype: :class:`~tamr_unify_client.models.dataset.resource.Dataset`
        """
        alias = self.api_path + "/recordPairs"
        return Dataset(self.client, None, alias)

    def pair_matching_model(self):
        """Machine learning model for pair-matching for this Mastering project.
        Learns from verified labels and predicts categorization labels for unlabeled pairs.

        Calling :func:`~tamr_unify_client.models.machine_learning_model.MachineLearningModel.predict`
        from this dataset will produce new (unpublished) clusters. These clusters
        are displayed on the "Clusters" page in the Unify UI.

        :returns: The machine learning model for pair-matching.
        :rtype: :class:`~tamr_unify_client.models.machine_learning_model.MachineLearningModel`
        """
        alias = self.api_path + "/recordPairsWithPredictions/model"
        return MachineLearningModel(self.client, None, alias)

    def high_impact_pairs(self):
        """High-impact pairs as a dataset. Unify labels pairs as "high-impact" if
        labeling these pairs would help it learn most quickly (i.e. "Active learning").

        High-impact pairs are displayed with a ⚡ lightning bolt icon on the
        "Pairs" page in the Unify UI.

        Call :func:`~tamr_unify_client.models.dataset.resource.Dataset.refresh` from
        this dataset to produce new high-impact pairs according to the latest
        pair-matching model.

        :returns: The high-impact pairs represented as a dataset.
        :rtype: :class:`~tamr_unify_client.models.dataset.resource.Dataset`
        """
        alias = self.api_path + "/highImpactPairs"
        return Dataset(self.client, None, alias)

    def record_clusters(self):
        """Record Clusters as a dataset. Unify clusters labeled pairs using pairs
        model. These clusters populate the cluster review page and get transient
        cluster ids, rather than published cluster ids (i.e., "Permanent Ids")

        Call :func:`~tamr_unify_client.models.dataset.resource.Dataset.refresh` from
        this dataset to generate clusters based on to the latest pair-matching model.

        :returns: The record clusters represented as a dataset.
        :rtype: :class:`~tamr_unify_client.models.dataset.resource.Dataset`
        """
        alias = self.api_path + "/recordClusters"
        return Dataset(self.client, None, alias)

    def published_clusters(self):
        """Published record clusters generated by Unify's pair-matching model.

        :returns: The published clusters represented as a dataset.
        :rtype: :class:`~tamr_unify_client.models.dataset.resource.Dataset`
        """

        unified_dataset = self.unified_dataset()

        # Replace this workaround with a direct API call once API
        # is fixed. APIs that need to work are: fetching the dataset and
        # being able to call refresh on resulting dataset. Until then, we grab
        # the dataset by constructing its name from the corresponding Unified Dataset's name
        name = unified_dataset.name + "_dedup_published_clusters"
        canonical = self.client.datasets.by_name(name)
        resource_json = canonical._data
        alias = self.api_path + "/publishedClusters"
        return Dataset.from_json(self.client, resource_json, alias)

    def published_clusters_configuration(self):
        """Retrieves published clusters configuration for this project.

        :returns: The published clusters configuration
        :rtype: :class:`~tamr_unify_client.models.project.cluster_configuration.PublishedClustersConfiguration`
        """
        alias = self.api_path + "/publishedClustersConfiguration"
        resource_json = self.client.get(alias).successful().json()
        return PublishedClustersConfiguration.from_json(
            self.client, resource_json, alias
        )

    def refresh_published_cluster_ids(self, **options):
        """
        Updates published clusters for this project.

        :param ``**options``: Options passed to underlying :class:`~tamr_unify_client.models.operation.Operation` .
                See :func:`~tamr_unify_client.models.operation.Operation.apply_options` .
        :returns: The operation to update published clusters.
        :rtype: :class:`~tamr_unify_client.models.operation.Operation`
        """
        path = self.api_path + "/allPublishedClusterIds:refresh"
        op_json = self.client.post(path).successful().json()
        op = Operation.from_json(self.client, op_json)
        return op.apply_options(**options)

    def estimate_pairs(self):
        """Returns pair estimate information for a mastering project

        :return: Pairs Estimate information.
        :rtype: :class:`~tamr_unify_client.models.project.estimated_pair_counts.EstimatedPairCounts`
        """
        alias = self.api_path + "/estimatedPairCounts"
        estimate_json = self.client.get(alias).successful().json()
        info = EstimatedPairCounts.from_json(self.client, estimate_json, api_path=alias)
        return info

    def record_clusters_with_data(self):
        """Project's unified dataset with associated clusters.

        :returns: The record clusters with data represented as a dataset
        :rtype: :class:`~tamr_unify_client.models.dataset.resource.Dataset`
        """
        unified_dataset = self.unified_dataset()

        # Replace this workaround with a direct API call once API
        # is fixed. APIs that need to work are: fetching the dataset and
        # being able to call refresh on resulting dataset. Until then, we grab
        # the dataset by constructing its name from the corresponding Unified Dataset's name
        name = unified_dataset.name + "_dedup_clusters_with_data"
        return self.client.datasets.by_name(name)

        # super.__repr__ is sufficient

    def published_clusters_with_data(self):
        """Project's unified dataset with associated clusters.
        :returns: The published clusters with data represented as a dataset
        :rtype :class `~tamr_unify_client.models.dataset.resource.Dataset`
        """

        unified_dataset = self.unified_dataset()
        name = unified_dataset.name + "_dedup_published_clusters_with_data"
        return self.client.datasets.by_name(name)

    def binning_model(self):
        """
        Binning model for this project.

        :return: Binning model for this project.
        :rtype: :class:`~tamr_unify_client.models.binning_model.BinningModel`
        """
        alias = self.api_path + "/binningModel"

        # Cannot get this resource and so we hard code
        resource_json = {"relativeId": alias}
        return BinningModel.from_json(self.client, resource_json, alias)
